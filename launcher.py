from __future__ import annotations

import os
import sys
import threading
import time
import webbrowser


def resource_path(name: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def open_browser() -> None:
    time.sleep(2.0)
    webbrowser.open("http://127.0.0.1:8501")


def main() -> None:
    from streamlit.web import cli as stcli

    app = resource_path("app.py")
    threading.Thread(target=open_browser, daemon=True).start()

    sys.argv = [
        "streamlit",
        "run",
        app,
        "--global.developmentMode=false",
        "--server.headless=true",
        "--server.address=127.0.0.1",
        "--server.port=8501",
        "--browser.gatherUsageStats=false",
    ]
    raise SystemExit(stcli.main())


if __name__ == "__main__":
    main()
