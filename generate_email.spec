# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['generate_email.py'],
    pathex=[],
    binaries=[],
    datas=[('credentials.json', '.')],
    hiddenimports=['google.auth.transport.requests', 'xml.parsers.expat', 'xml.etree.ElementTree', 'xml.dom.minidom'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'numpy.distutils', 'PIL', 'IPython',
    'jupyter', 'notebook', 'sphinx', 'pytest', 'setuptools',
    'distutils', 'email.test', 'unittest', 'doctest'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='generate_email',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='drafticon.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='generate_email',
)
