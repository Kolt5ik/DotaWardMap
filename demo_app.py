"""Run the real application with deterministic, offline demonstration data.

Start with: python -m streamlit run demo_app.py
This entry point never requests a real player's data. app.py is unchanged.
"""
from __future__ import annotations

import json
import runpy
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import requests
import streamlit as st

ROOT = Path(__file__).resolve().parent
DEMO_ACCOUNT = 12345678
WARDMAP = json.loads((ROOT / "docs" / "demo-data.json").read_text(encoding="utf-8"))
PLAYER = {"profile": {"personaname": "DEMO • Учебные данные / Sample data"}}


def demo_request(url, *args, **kwargs):
    """Serve only the app's documented API routes; reject all other requests."""
    prefix = "https://api.opendota.com/api/players/"
    if not url.startswith(prefix):
        raise requests.RequestException(
            "Демо работает без сети. Используй числовой ID; данные останутся учебными."
        )
    route = url[len(prefix):].strip("/").split("/")
    if not route[0].isdigit():
        raise requests.RequestException("Демо принимает числовой ID")
    if len(route) == 1:
        payload = PLAYER
    elif route[1:] == ["wardmap"]:
        payload = WARDMAP
    elif route[1:] == ["refresh"]:
        payload = {"demo": True}
    else:
        raise requests.RequestException("Этот запрос не поддерживается демо")
    response = requests.Response()
    response.status_code = 200
    response.url = url
    response._content = json.dumps(payload).encode("utf-8")
    response.headers["Content-Type"] = "application/json"
    return response


if "account_id" not in st.session_state:
    rows = [
        {"type": kind, "x": float(x), "y": float(y), "count": float(count)}
        for kind, field in [("Observer", "obs"), ("Sentry", "sen")]
        for x, ys in WARDMAP[field].items()
        for y, count in ys.items()
    ]
    st.session_state.update(
        account_id=DEMO_ACCOUNT,
        player=PLAYER,
        df=pd.DataFrame(rows, columns=["type", "x", "y", "count"]),
        source_profile=str(DEMO_ACCOUNT),
        loaded_limit=100,
    )

# Patches exist only while this demo entry point renders the real app.
# Changing the numeric profile or match limit intentionally keeps sample data.
with patch.object(requests, "get", demo_request), patch.object(requests, "post", demo_request):
    runpy.run_path(str(ROOT / "app.py"), run_name="__main__")
