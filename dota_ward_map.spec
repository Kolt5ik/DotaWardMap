# PyInstaller spec for the Windows desktop launcher.
from PyInstaller.utils.hooks import collect_all, collect_submodules

streamlit_datas, streamlit_binaries, streamlit_hidden = collect_all("streamlit")
plotly_datas, plotly_binaries, plotly_hidden = collect_all("plotly")

hiddenimports = sorted(set(streamlit_hidden + plotly_hidden + collect_submodules("streamlit.web") + ["requests", "pandas", "PIL.Image", "kaleido"]))

datas = streamlit_datas + plotly_datas + [
    ("app.py", "."),
    ("assets", "assets"),
    ("README.md", "."),
    ("LICENSE", "."),
]

binaries = streamlit_binaries + plotly_binaries


a = Analysis(
    ["launcher.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="DotaWardMap",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)
