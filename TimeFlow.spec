# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    # Hier werden die Assets eingebunden. Tuple-Format ist (Quelle, Ziel)
    datas=[('timeflow_assets', 'timeflow_assets')],
    hiddenimports=[],
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
    # Für OneFile müssen binaries, zipfiles und datas HIER rein:
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TimeFlow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # Kein schwarzes Konsolenfenster
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Windows Icon (wird auf Mac ignoriert oder fallback)
    icon='timeflow_assets/TimeFlowIcon.ico'
)