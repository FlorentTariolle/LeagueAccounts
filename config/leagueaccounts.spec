# -*- mode: python ; coding: utf-8 -*-

# When building, use: pyinstaller --distpath ../../build/dist leagueaccounts.spec

a = Analysis(
    ['../src/leagueaccounts/main.py'],
    pathex=['../src'],
    binaries=[],
    datas=[
        ('../assets/icons/icon.ico', 'assets/icons'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='leagueaccounts',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['../assets/icons/icon.ico'],
)
