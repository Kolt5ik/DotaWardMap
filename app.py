from __future__ import annotations

import base64
import os
import sys
import threading
import html
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
import numpy as np
import re
from urllib.parse import quote, urlparse

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

API = "https://api.opendota.com/api"
MAP_PATH = Path(__file__).resolve().parent / "assets" / "map_7_39.png"
MAP_W = MAP_H = 1024

@st.cache_data
def local_map_uri():
    # Validate bytes; never render an error response as the map background.
    with Image.open(MAP_PATH) as image:
        image.verify()
    return "data:image/png;base64," + base64.b64encode(MAP_PATH.read_bytes()).decode()

st.set_page_config(page_title="Dota 2 Ward Map", page_icon="🗺️", layout="wide")

st.markdown(
    """
    <style>
    .block-container { max-width: 1500px; padding-top: 1.5rem; }
    div[data-testid="stMetric"] { background: #111827; border: 1px solid #263244; border-radius: 12px; padding: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=120)
def api_get(path: str, params: dict | None = None):
    try:
        response = requests.get(f"{API}{path}", params=params, timeout=25)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        detail = ""
        try:
            detail = response.text[:500]
        except Exception:
            pass
        raise RuntimeError(f"OpenDota HTTP {response.status_code}. {detail}") from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"Не удалось подключиться к OpenDota: {exc}") from exc


def api_post(path: str, params: dict | None = None):
    try:
        response = requests.post(f"{API}{path}", params=params, timeout=25)
        response.raise_for_status()
        return response.json() if response.content else None
    except requests.HTTPError as exc:
        detail = response.text[:500] if response is not None else ""
        raise RuntimeError(f"OpenDota HTTP {response.status_code}. {detail}") from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"Не удалось подключиться к OpenDota: {exc}") from exc


def steam64_to_account_id(steam64: int) -> int:
    """Convert a SteamID64 to OpenDota's Steam32 account_id."""
    return steam64 - 76561197960265728


def extract_account_id(value: str) -> int | None:
    """Extract an OpenDota/Steam32 account_id or convert a SteamID64."""
    value = value.strip()
    if not value:
        return None

    # Plain numeric ID: accept both Steam32 and SteamID64.
    if value.isdigit():
        n = int(value)
        if n >= 76561197960265728:
            return steam64_to_account_id(n)
        if n > 0:
            return n
        return None

    parsed = urlparse(value if "://" in value else "https://" + value)
    path = parsed.path.strip("/")

    # /profiles/7656119... (SteamID64) or /profiles/<steam32>
    m = re.search(r"(?:^|/)profiles/(\d+)(?:/|$)", path, re.I)
    if m:
        return extract_account_id(m.group(1))

    # OpenDota: /players/<steam32>
    m = re.search(r"(?:^|/)players/(\d+)(?:/|$)", path, re.I)
    if m:
        return int(m.group(1))

    return None


def valid_steam_account_id(value: str) -> int:
    steam64 = int(value)
    account = steam64_to_account_id(steam64)
    if not 0 < account <= 4294967295:
        raise ValueError("Некорректный SteamID профиля")
    return account


@st.cache_data(ttl=300)
def resolve_steam_vanity(vanity: str) -> tuple[int, dict | None]:
    """Resolve the exact custom profile using Steam XML, then profile HTML.

    Never search by display name: it need not match the custom URL.
    Successful resolutions are cached briefly; errors are not cached.
    """
    profile_url = f"https://steamcommunity.com/id/{quote(vanity, safe='')}/"
    headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}
    failures = []
    try:
        response = requests.get(profile_url, params={"xml": "1"}, headers=headers, timeout=15)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        if root.tag == "profile":
            value = root.findtext("steamID64")
            if value:
                return valid_steam_account_id(value.strip()), None
        failures.append("Steam XML не содержит ID профиля")
    except (requests.RequestException, ET.ParseError, ValueError):
        failures.append("Steam XML недоступен")

    try:
        response = requests.get(profile_url, headers=headers, timeout=15)
        response.raise_for_status()
        content = html.unescape(response.text)
        # Only read this profile's data; unrelated IDs on the page are ignored.
        profile_data = re.search(r"g_rgProfileData\s*=\s*(\{[^\n]+\})", content)
        if profile_data:
            match = re.search(r'"steamid"\s*:\s*"(\d{17})"', profile_data.group(1))
            if match:
                return valid_steam_account_id(match.group(1)), None
        failures.append("Steam HTML не содержит ID профиля")
    except (requests.RequestException, ValueError):
        failures.append("Страница Steam недоступна")

    raise ValueError(
        f"Не удалось получить SteamID для /id/{vanity}: {'; '.join(failures)}. "
        "Повтори позже или используй числовую ссылку /profiles/7656119... ."
    )


def resolve_profile(value: str) -> tuple[int, dict | None]:
    value = value.strip()
    account_id = extract_account_id(value)
    if account_id is not None:
        return account_id, None

    parsed = urlparse(value if "://" in value else "https://" + value)
    host = parsed.netloc.lower().split(":")[0]
    path = parsed.path.strip("/")
    parts = [p for p in path.split("/") if p]

    if host in {"steamcommunity.com", "www.steamcommunity.com"}:
        if len(parts) >= 2 and parts[0].lower() == "id" and parts[1]:
            return resolve_steam_vanity(parts[1])

    raise ValueError(
        "Не удалось определить профиль. Используй один из форматов: "
        "https://steamcommunity.com/profiles/7656119..., "
        "https://steamcommunity.com/id/username, SteamID64/Steam32 "
        "или https://www.opendota.com/players/12345678."
    )


def xy_from_key(key) -> tuple[float, float] | None:
    if isinstance(key, (list, tuple)) and len(key) >= 2:
        try:
            return float(key[0]), float(key[1])
        except (TypeError, ValueError):
            return None
    if isinstance(key, str):
        nums = re.findall(r"-?\d+(?:\.\d+)?", key)
        if len(nums) >= 2:
            return float(nums[0]), float(nums[1])
    return None


def _to_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_wardmap(payload: dict) -> pd.DataFrame:
    """Convert OpenDota wardmap's nested {x: {y: count}} format to rows.

    OpenDota represents wardmap coordinates as a nested object: the outer key
    is one coordinate and the inner key is the other coordinate. Older code
    treated the outer key as a complete ``x,y`` string, which silently dropped
    all points.
    """
    rows = []
    for kind, field in (("Observer", "obs"), ("Sentry", "sen")):
        data = payload.get(field, {}) or {}

        if isinstance(data, dict):
            for x_key, y_values in data.items():
                # Normal OpenDota format: {"x": {"y": count}}
                x = _to_number(x_key)
                if x is not None and isinstance(y_values, dict):
                    for y_key, count in y_values.items():
                        y = _to_number(y_key)
                        if y is None:
                            continue
                        try:
                            count_num = float(count)
                        except (TypeError, ValueError):
                            count_num = 1.0
                        rows.append({"type": kind, "x": x, "y": y, "count": count_num})
                    continue

                # Compatibility with a possible flat format: {"x,y": count}.
                xy = xy_from_key(x_key)
                if xy is not None:
                    try:
                        count_num = float(y_values)
                    except (TypeError, ValueError):
                        count_num = 1.0
                    rows.append({"type": kind, "x": xy[0], "y": xy[1], "count": count_num})

        elif isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                x = _to_number(item.get("x"))
                y = _to_number(item.get("y"))
                if x is None or y is None:
                    continue
                try:
                    count_num = float(item.get("count", 1))
                except (TypeError, ValueError):
                    count_num = 1.0
                rows.append({"type": kind, "x": x, "y": y, "count": count_num})

    return pd.DataFrame(rows, columns=["type", "x", "y", "count"])


def world_to_image(x: float, y: float) -> tuple[float, float]:
    """OpenDota grid: (64,64) southwest, (191,191) northeast.

    Return image coordinates: x rightwards, y downwards.
    """
    return (x - 64) / 127 * MAP_W, (191 - y) / 127 * MAP_H


def density_trace(part):
    axis = np.linspace(0, MAP_H, 128)
    gx, gy = np.meshgrid(axis, axis)
    density = np.zeros_like(gx, dtype=float)
    coords = part.apply(lambda r: world_to_image(r.x, r.y), axis=1, result_type="expand")

    for px, py, count in zip(coords[0], MAP_H - coords[1], part["count"]):
        density += max(0, float(count)) * np.exp(
            -((gx - px) ** 2 + (gy - py) ** 2) / (2 * 22.0 ** 2)
        )

    peak = float(density.max())
    if peak > 0:
        density = (density / peak) ** 0.72

    return go.Heatmap(
        x=axis, y=axis, z=density, zmin=0, zmax=1,
        zsmooth="best", showscale=False, hoverinfo="skip",
        colorscale=[
            [0.00, "rgba(255,220,70,0)"],
            [0.06, "rgba(255,220,70,0)"],
            [0.16, "rgba(255,220,70,0.18)"],
            [0.42, "rgba(255,150,35,0.34)"],
            [0.72, "rgba(255,70,35,0.58)"],
            [1.00, "rgba(255,35,35,0.82)"],
        ],
    )

def build_map(df: pd.DataFrame, show_obs: bool, show_sentry: bool, heatmap: bool, size: int, opacity: float, heat_type: str = "Observer", show_points_on_heatmap: bool = False):
    allowed = []
    if show_obs:
        allowed.append("Observer")
    if show_sentry:
        allowed.append("Sentry")
    plot = df[df["type"].isin(allowed)].copy()

    fig = go.Figure()
    fig.add_layout_image(
        dict(
            source=local_map_uri(),
            xref="x", yref="y", x=0, y=MAP_H,
            sizex=MAP_W, sizey=MAP_H, sizing="stretch",
            opacity=1.0, layer="below",
        )
    )

    if heatmap:
        heat_source = plot[plot["type"] == heat_type]
        if not heat_source.empty:
            fig.add_trace(density_trace(heat_source))

    for kind, symbol, label in [
        ("Observer", "circle", "Observer"),
        ("Sentry", "square", "Sentry"),
    ]:
        part = plot[plot["type"] == kind].copy()
        if part.empty or (heatmap and not show_points_on_heatmap):
            continue
        coords = part.apply(lambda r: world_to_image(r.x, r.y), axis=1, result_type="expand")
        part["px"], part["py"] = coords[0], coords[1]
        marker_size = (part["count"].clip(lower=1) ** 0.5 * size).tolist()
        fig.add_trace(
            go.Scatter(
                x=part["px"], y=MAP_H - part["py"], mode="markers", name=label,
                marker=dict(color="#ffe14b" if kind == "Observer" else "#32b7ff", symbol=symbol, size=marker_size, opacity=opacity, line=dict(width=1, color="#ffffff")),
                customdata=part[["x", "y", "count"]],
                hovertemplate=(
                    f"<b>{label}</b><br>"
                    "X: %{customdata[0]:.0f}<br>Y: %{customdata[1]:.0f}<br>"
                    "Постановок в этой точке: %{customdata[2]:.0f}<extra></extra>"
                ),
            )
        )

    fig.update_xaxes(range=[0, MAP_W], visible=False, fixedrange=False)
    fig.update_yaxes(range=[0, MAP_H], visible=False, fixedrange=False, scaleanchor="x", scaleratio=1)
    fig.update_layout(
        height=760, margin=dict(l=0, r=0, t=0, b=0),
        dragmode="zoom",
        paper_bgcolor="#0b0f14", plot_bgcolor="#0b0f14",
        legend=dict(orientation="h", y=1.01, x=0, font=dict(color="#e5e7eb")),
        uirevision="ward-map-7.39", hovermode="closest",
    )
    return fig


def png_bytes(fig) -> bytes | None:
    try:
        return fig.to_image(format="png", width=1600, height=1000, scale=2)
    except Exception:
        return None


def desktop_exit_enabled() -> bool:
    # Only a frozen executable started by our launcher may terminate itself.
    return bool(getattr(sys, "frozen", False)) and os.environ.get("DOTAWARDMAP_DESKTOP_PID") == str(os.getpid())


def schedule_desktop_exit() -> bool:
    if not desktop_exit_enabled():
        return False
    # Streamlit runs the page in a worker thread. SystemExit would only stop
    # that thread; terminate this executable after sending the final UI update.
    timer = threading.Timer(2.0, os._exit, args=(0,))
    timer.daemon = True
    timer.start()
    return True


def footer():
    st.divider()
    st.caption("Open source • OpenDota API • Карта и игровые материалы © Valve • Не связано с Valve")
    st.markdown('<div style="text-align:center;opacity:.45;font-size:.78rem"><a href="https://github.com/Kolt5ik" style="color:inherit;text-decoration:none">GitHub · Kolt5ik</a></div>', unsafe_allow_html=True)


st.title("🗺️ Dota 2 Ward Map")
st.caption("v9 • Локальная карта 7.39 • Варды за последние N матчей")
with st.sidebar:
    if desktop_exit_enabled():
        if st.button("Завершить приложение", key="desktop_exit", use_container_width=True,
                     help="Останавливает EXE и освобождает порт. Вкладку затем можно закрыть."):
            st.session_state["desktop_exit_requested"] = True
        st.divider()
    st.header("Профиль")
    profile_input = st.text_input("Steam / OpenDota / account ID", placeholder="1324728778")
    matches_limit = st.slider("Матчей учитывать", 1, 1000, 100)
    load = st.button("Смотреть профиль", type="primary", use_container_width=True)
    refresh = st.button("Обновить историю OpenDota", use_container_width=True)
    st.divider()
    use_heatmap = st.checkbox("Тепловой слой", False)
    if use_heatmap:
        heat_type = st.radio("Плотность для", ["Observer", "Sentry"], horizontal=True)
        show_points_on_heatmap = st.checkbox("Показать точки поверх", False)
        show_obs = show_sentry = True
        point_size, point_opacity = 9, 0.8
    else:
        heat_type, show_points_on_heatmap = "Observer", False
        show_obs = st.checkbox("🟡 Observer", True)
        show_sentry = st.checkbox("🔵 Sentry", True)
        point_size = st.slider("Размер точек", 2, 30, 9)
        point_opacity = st.slider("Непрозрачность точек", 0.1, 1.0, 0.8)

if st.session_state.get("desktop_exit_requested") and desktop_exit_enabled():
    st.success("Приложение завершается. Эту вкладку можно закрыть.")
    if not st.session_state.get("desktop_exit_scheduled"):
        st.session_state["desktop_exit_scheduled"] = schedule_desktop_exit()
    st.stop()

if load or refresh:
    source = profile_input.strip() or st.session_state.get("source_profile", "")
    try:
        if not source:
            raise ValueError("Вставь ссылку или ID игрока")
        with st.spinner("Получаю профиль и карту вардов…"):
            account, _ = resolve_profile(source)
            if refresh:
                api_post(f"/players/{account}/refresh")
                api_get.clear()
                st.info("Обновление истории запрошено и выполняется асинхронно. Если данные ещё не обновились, позже нажми «Смотреть профиль» снова.")
            player = api_get(f"/players/{account}")
            wardmap = api_get(f"/players/{account}/wardmap", {"limit": matches_limit, "significant": 0})
            df = normalize_wardmap(wardmap)
            st.session_state.update(account_id=account, player=player, df=df,
                                    source_profile=source, loaded_limit=matches_limit)
    except Exception as exc:
        st.error(f"Не удалось загрузить профиль: {exc}")

if "account_id" not in st.session_state:
    st.info("Вставь профиль слева, укажи число последних матчей и нажми «Смотреть профиль».")
    st.plotly_chart(build_map(normalize_wardmap({}), True, True, False, 9, .8), use_container_width=True,
                    config={"displayModeBar": False, "scrollZoom": False, "doubleClick": "reset"})
    footer()
    st.stop()

profile = st.session_state.player.get("profile") or {}
st.subheader(profile.get("personaname") or f"Игрок {st.session_state.account_id}")
st.caption(f"Steam32: {st.session_state.account_id} • Матчей в запросе: {st.session_state.loaded_limit} • обычные + нестандартные матчи")
if profile.get("profileurl", "").startswith("https://steamcommunity.com/"):
    st.link_button("Открыть Steam-профиль", profile["profileurl"])
if matches_limit != st.session_state.loaded_limit:
    st.info("Число матчей изменено. Нажми «Смотреть профиль», чтобы обновить карту.")
df = st.session_state.df
cols = st.columns(3)
obs = int(df.loc[df.type == "Observer", "count"].sum())
sen = int(df.loc[df.type == "Sentry", "count"].sum())
cols[0].metric("Observer", obs)
cols[1].metric("Sentry", sen)
cols[2].metric("Всего", obs + sen)
st.caption(
    "ⓘ Статистика может быть неполной: учитываются только варды из матчей, разобранных OpenDota.",
    help=(
        "Выбранное число матчей не гарантирует наличие данных за каждый матч. "
        "Если OpenDota не разобрал реплей, варды из него не попадут на карту."
    ),
)
if df.empty:
    st.warning("OpenDota не вернул координаты вардов. Попробуй увеличить число матчей или обновить историю. Наличие матчей не гарантирует наличие данных разбора реплеев.")
st.caption("Зажми левую кнопку и выдели область для приближения. Двойной клик — сброс. Колесо не масштабирует карту.")
st.caption("Фон фиксирован на патче 7.39. Для матчей других патчей ландшафт может отличаться.")
fig = build_map(df, show_obs, show_sentry, use_heatmap, point_size, point_opacity, heat_type, show_points_on_heatmap)
st.plotly_chart(fig, use_container_width=True,
                config={"displaylogo": False, "displayModeBar": False, "scrollZoom": False, "doubleClick": "reset"})
if not df.empty:
    st.download_button("Скачать данные CSV", df.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"{st.session_state.account_id}_wards.csv", mime="text/csv")
    if st.button("Подготовить PNG карты"):
        png = png_bytes(fig)
        if png:
            st.download_button("Скачать карту PNG", png, file_name="ward_map.png", mime="image/png")
        else:
            st.warning("Экспорт PNG недоступен. CSV и сама карта продолжают работать.")
    with st.expander("Данные вардов"):
        st.dataframe(df, hide_index=True, use_container_width=True)
footer()
