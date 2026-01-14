# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

# 1. Analyse (Gleich für alle)
a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('timeflow_assets', 'timeflow_assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# --- UNTERSCHEIDUNG WINDOWS vs. MAC ---

if sys.platform == 'darwin':
    # === MACOS BUILD (App Bundle) ===
    exe = EXE(
        pyz,
        a.scripts,
        [], # Keine Binaries hier, wir sammeln sie unten
        exclude_binaries=True,
        name='TimeFlow',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=True, # Wichtig für Mac Drag/Drop
        target_arch='arm64', # oder 'x86_64' oder None für Auto
        codesign_identity=None,
        entitlements_file=None,
    )
    
    # Sammelt alles in einen Ordner
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='TimeFlow',
    )
    
    # Macht daraus eine .app
    app = BUNDLE(
        coll,
        name='TimeFlow.app',
        icon='timeflow_assets/TimeFlowIcon.png', # Mac mag png oder icns
        bundle_identifier='com.conraoi.timeflow',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False'
        }
    )

else:
    # === WINDOWS BUILD (Single .exe) ===
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='TimeFlow', # Erzeugt TimeFlow.exe
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='timeflow_assets/TimeFlowIcon.ico' # Windows braucht .ico
    )