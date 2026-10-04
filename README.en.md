<p align="center"><img src="docs/assets/cover.svg" alt="DotaWardMap — schematic ward placement graphic" width="100%"></p>

<p align="center">
<a href="https://github.com/Kolt5ik/DotaWardMap/releases/latest"><img src="https://img.shields.io/github/v/release/Kolt5ik/DotaWardMap?style=flat-square&color=dda94b" alt="Latest release"></a>
<a href="https://github.com/Kolt5ik/DotaWardMap/actions/workflows/build-windows.yml"><img src="https://github.com/Kolt5ik/DotaWardMap/actions/workflows/build-windows.yml/badge.svg" alt="Windows build"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-32b7ff?style=flat-square" alt="Code license: MIT"></a>
</p>

<p align="center"><strong>See where you place wards. Find recurring positions. Review them with your team.</strong></p>
<p align="center"><a href="https://github.com/Kolt5ik/DotaWardMap/releases/latest/download/DotaWardMap.exe"><img src="docs/assets/download-windows-en.svg" width="260" alt="Download for Windows"></a></p>
<p align="center"><a href="#quick-start">Quick start</a> · <a href="#features">Features</a> · <a href="README.md">Русский</a></p>

## See the application

![Actual DotaWardMap interface: heatmap and point overlay](docs/assets/preview.gif)

*Animated overview of two actual v9.0.4 screenshots: Sentry density, then Observer/Sentry positions over the layer.*

DotaWardMap is an open-source Dota 2 ward placement analyzer built with Python, Streamlit and Plotly. It runs on your computer and opens its interface in a browser. Internet access is needed to fetch OpenDota data; Steam and Dota 2 do not need to be installed.

> OpenDota data can be incomplete. Requesting 100 matches does not guarantee ward data for all 100. The background map is fixed to **patch 7.39**.

## Contents

- [Features](#features)
- [See the application](#see-the-application)
- [Interface preview](#interface-preview)
- [Quick start](#quick-start)
- [Using the map](#using-the-map)
- [Data and limitations](#data-and-limitations)
- [Contributing](#contributing)
- [License and credits](#license-and-credits)

## Features

| Feature | Description |
| --- | --- |
| Profile input | Steam profile URL, custom /id/ URL, SteamID64, numeric account ID or OpenDota player URL |
| Recent matches | Aggregated data for a requested limit of 1–1000 matches; default 100 |
| Ward types | Observer and Sentry filters in point mode; separate density selection in heatmap mode |
| Smooth heatmap | Count-weighted density with transparent low-density areas |
| Optional overlay | Show exact positions over the heatmap |
| Interactive map | Drag to select a zoom area, double-click to reset; wheel zoom disabled |
| Export | Aggregated CSV data and optional PNG with the selected layers |
| Windows EXE | Bundled Python runtime and an exit button that stops the local server |

<details>
<summary><strong>Optional: try the interactive demo</strong></summary>

Download [interactive-demo.html](docs/interactive-demo.html) using **Download raw file** and open it in your browser. No installation, server or network is required. Explore points, Observer/Sentry density, overlays, zoom, CSV and the guided tour.

The map uses the application's renderer with **sample data**. The controls are a presentation shell, not the complete Streamlit interface. The cover above is a schematic graphic; screenshots below show the real application.

To run the actual Streamlit interface offline with the same fixtures, install dependencies and run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run demo_app.py --server.address=127.0.0.1 --browser.gatherUsageStats=false
```

On Linux/macOS, use `.venv/bin/python`. All numeric profile IDs and match limits keep the same sample dataset. No real Steam or OpenDota requests are made. [Demo guide and walkthrough](docs/demo.md#english).

</details>

## Interface preview

![Sentry heatmap in DotaWardMap](docs/assets/heatmap.png)

*Author's v9.0.4 screenshot: Sentry density on the fixed 7.39 map. Displayed totals may represent incomplete OpenDota data.*

<details>
<summary>Show the optional point overlay</summary>

![Observer and Sentry positions over the heatmap](docs/assets/points-overlay.png)

</details>

## Quick start

### Windows EXE

1. Open the [latest release](https://github.com/Kolt5ik/DotaWardMap/releases/latest).
2. Under **Assets**, download **DotaWardMap.exe**. The Source code archives are for development.
3. Run it. The browser opens [127.0.0.1:8501](http://127.0.0.1:8501).
4. Paste a profile, set the match limit and click **«Смотреть профиль»** (View profile).
5. Click **«Завершить приложение»** (Exit application) when finished. Closing the browser tab does not stop the server.

The application interface is currently in Russian.

### From source

Use **Python 3.12**, the version used by the Windows build. Download and extract the [source ZIP](https://github.com/Kolt5ik/DotaWardMap/archive/refs/heads/main.zip), or clone the repository. Run these commands from the folder containing `app.py` and `requirements.txt`.

**Windows / PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address=127.0.0.1 --browser.gatherUsageStats=false
```

**Linux / macOS:**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py --server.address=127.0.0.1 --browser.gatherUsageStats=false
```

No environment activation is needed. Keep the terminal open; press **Ctrl+C** to stop. On Ubuntu/Debian, installing the system's `python3-venv` package may be necessary.

To build the Windows EXE locally, run `build_exe.bat` on Windows with Python installed. The output is `dist/DotaWardMap.exe`. Manual GitHub Actions builds produce an artifact; pushing a `v*` tag builds and publishes a release.

## Using the map

1. Enter a numeric account ID, SteamID64, a full `steamcommunity.com/profiles/…` or `steamcommunity.com/id/…` URL, or an `opendota.com/players/…` URL.
2. Click **«Смотреть профиль»**. After changing the match limit, click again to reload.
3. In point mode, yellow circles are Observer and blue squares are Sentry. Repeated placements at one coordinate share a marker; hover for the count.
4. Enable **«Тепловой слой»** (Heatmap), choose Observer or Sentry, and optionally enable **«Показать точки поверх»** (Show points on top). The point overlay contains both types.
5. Drag with the left mouse button to zoom into a rectangle; double-click to reset.
6. Use **«Скачать данные CSV»** to export all loaded aggregated data. Use **«Подготовить PNG карты»** to prepare an image, then download it.

Heatmap colors show relative placement density, not vision range or ward effectiveness. Each heatmap is normalized independently, so equal colors in separate results do not mean equal placement counts. Browser zoom gestures are not passed to the server-side PNG export; use a screenshot to capture a zoomed area.

## Data and limitations

The app requests `GET https://api.opendota.com/api/players/{account_id}/wardmap` with `limit=N` and `significant=0`. It converts nested Observer/Sentry coordinate counts into rows of `type,x,y,count`. Metrics sum `count`; they do not count rows.

- Unparsed replays can be missing. The returned total is not guaranteed to cover every requested match.
- Refreshing history is asynchronous and does not guarantee replay parsing.
- The fixed 7.39 map may differ from terrain in other patches; alignment of all objects has not been verified against real replays.
- Individual match selection, placement timestamps and ward effectiveness are not available.
- The query includes both regular and nonstandard matches without a separate UI filter.
- CSV exports both ward types regardless of display filters.
- PNG export depends on Plotly/Kaleido compatibility. If it fails, CSV and the map remain usable.
- Custom Steam URLs are resolved from that exact profile; a display-name search is never used as an identity substitute.
- Requests use OpenDota and, for custom URLs, Steam Community. No Steam login or API key is required by this implementation.

For an empty map, try requesting a larger match limit or refreshing history, then load again later. For a failed custom URL, try the numeric SteamID64 or account ID. If the EXE seems to run an old version, stop the old server before launching the new file. For PNG issues, export CSV or use the browser's screenshot tools.

Additional Russian guides: [usage](docs/usage.md), [installation](docs/installation.md), [data](docs/data.md), [troubleshooting](docs/troubleshooting.md), [contribution workflow](CONTRIBUTING.md).

## Contributing

Bug reports, ideas and documentation improvements are welcome. Use the [issue templates](https://github.com/Kolt5ik/DotaWardMap/issues/new/choose), work on a separate branch, verify the change and open a pull request against `main`.

Include the app version, operating system, reproduction steps and relevant error text. Remove private information from screenshots. For UI changes, attach before/after screenshots. For data changes, verify coordinate conversion and count aggregation. The repository does not currently contain an automated test suite.

## License and credits

Project code and documentation use the [MIT License](LICENSE). Valve owns the Dota 2 map and game materials; these are excluded from MIT. See [map attribution](assets/README.md).

Data: [OpenDota](https://www.opendota.com/). UI: [Streamlit](https://streamlit.io/) and [Plotly](https://plotly.com/python/). Inspired by [DOTAWardFinder](https://github.com/NadimKawwa/DOTAWardFinder). Maintained by [Kolt5ik](https://github.com/Kolt5ik).

An independent community tool, not an official Valve or OpenDota product.
