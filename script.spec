# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['script.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['ipython', 'backcall', 'decorator', 'jedi', 'parso', 'matplotlib-inline', 'pickleshare', 'prompt_toolkit', 'wcwidth', 'Pygments', 'stack-data', 'asttokens', 'six', 'executing', 'pure-eval', 'traitlets', 'nbconvert', 'beautifulsoup4', 'soupsieve', 'bleach', 'webencodings', 'defusedxml', 'Jinja2', 'MarkupSafe', 'mistune', 'nbclient', 'jupyter_client', 'python-dateutil', 'pyzmq', 'tornado', 'fastjsonschema', 'jsonschema', 'attrs', 'jsonschema-specifications', 'referencing', 'rpds-py', 'pandocfilters', 'tinycss2'],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [('O', None, 'OPTION'), ('O', None, 'OPTION')],
    name='script',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['D:\\Coding\\Python\\AnotherpySirilScript\\icon.ico'],
)
