# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

# --- 1. GEMEINSAME ANALYSE ---
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

# --- 2. PLATTFORM-UNTERSCHEIDUNG ---

if sys.platform == 'darwin':
    # =========================================================
    # MACOS BUILD -> .app BUNDLE
    # =========================================================
    print(">>> BUILDING FOR MACOS (App Bundle with Entitlements)")
    
    exe = EXE(
        pyz,
        a.scripts,
        [], # Binaries werden hier EXKLUDIERT (für OneDir/Bundle Modus)
        exclude_binaries=True,
        name='TimeFlow',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=True, 
        target_arch='arm64', 
        
        # --- SICHERHEITS-FEATURES ---
        codesign_identity='-', 
        entitlements_file='entitlements.plist', 
    )
    
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
    
    app = BUNDLE(
        coll,
        name='TimeFlow.app',
        icon='timeflow_assets/TimeFlowIcon.png',
        bundle_identifier='com.conraoi.timeflow', 
        
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False',
            'NSMicrophoneUsageDescription': 'TimeFlow benötigt Zugriff auf das Mikrofon für die Lärmampel.',
            'CFBundleShortVersionString': '1.0.5',
        }
    )

else:
    # =========================================================
    # WINDOWS BUILD -> SINGLE FILE .EXE
    # =========================================================
    print(">>> BUILDING FOR WINDOWS (OneFile .exe)")

    exe = EXE(
        pyz,
        a.scripts,
        a.binaries, # Alles in EINE Datei packen (required for workflow to find dist/TimeFlow.exe)
        a.zipfiles,
        a.datas,
        [],
        name='TimeFlow.exe',
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
        icon='timeflow_assets/TimeFlowIcon.ico'
    )
