# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icons/Lexi.png', '.'),
        ('icons/Lexi.icns', 'icons'),
        ('ui/*.py', 'ui'),
        ('ui/components/*.py', 'ui/components'),
        ('models/*.py', 'models'),
    ],
    hiddenimports=[
        'nltk',
        'nltk.stem.wordnet',
        'nltk.corpus',
        'nltk.tokenize',
        'docx',
        'docx.shared',
        'docx.enum.text',
        'python-docx',
        'requests',
        'ui',
        'ui.main_window',
        'ui.components',
        'ui.components.sentence_widget',
        'ui.components.settings_panel',
        'ui.components.word_input_panel',
        'models',
        'models.config',
        'models.translations',
        'models.api_service',
        'models.word_processor',
        'models.updater',
        'yaml',
        'pyyaml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LexiGen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LexiGen',
)

app = BUNDLE(
    coll,
    name='LexiGen.app',
    icon='icons/Lexi.icns',
    bundle_identifier='com.michaelqiu.lexigen',
    info_plist={
        'CFBundleShortVersionString': '1.6.0',
        'CFBundleVersion': '1.6.0',
        'NSHighResolutionCapable': True,
        'CFBundleDisplayName': 'LexiGen',
        'CFBundleName': 'LexiGen',
        'NSRequiresAquaSystemAppearance': False,
        'LSMinimumSystemVersion': '10.13.0',
    },
)
