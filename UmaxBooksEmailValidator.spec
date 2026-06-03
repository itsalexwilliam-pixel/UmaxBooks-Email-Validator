# -*- mode: python ; coding: utf-8 -*-
# UmaxBooks Power Email Validation — PyInstaller spec
# Single-file windowed EXE — fully self-contained, no dependencies needed

# collect_all pulls in EVERY module, binary DLL, and data file for a package
# This is the ONLY reliable way to bundle numpy/pandas C-extensions
from PyInstaller.utils.hooks import collect_all, collect_submodules

# --- Collect everything for packages with C-extensions ---
numpy_datas,   numpy_bins,   numpy_hidden   = collect_all('numpy')
pandas_datas,  pandas_bins,  pandas_hidden  = collect_all('pandas')
dns_datas,     dns_bins,     dns_hidden     = collect_all('dns')
pillow_datas,  pillow_bins,  pillow_hidden  = collect_all('PIL')
openpyxl_data, openpyxl_bin, openpyxl_hid  = collect_all('openpyxl')

a = Analysis(
    ['gui_app.py'],
    pathex=[],

    binaries=numpy_bins + pandas_bins + dns_bins + pillow_bins + openpyxl_bin,

    datas=(
        numpy_datas + pandas_datas + dns_datas + pillow_datas + openpyxl_data
        + [
            ('Power.png',    '.'),   # app logo
            ('app_icon.ico', '.'),   # window icon
        ]
    ),

    hiddenimports=(
        numpy_hidden + pandas_hidden + dns_hidden + pillow_hidden + openpyxl_hid
        + [
            # local modules
            'email_validator',
            'parallel_processor',
            'advanced_reporter',
            'domain_reputation',
            # dns sub-modules used during email validation
            'dns.resolver',
            'dns.exception',
            'dns.rdatatype',
            'dns.rdataclass',
            'dns.rdtypes',
            'dns.rdtypes.ANY',
            'dns.rdtypes.ANY.MX',
            'dns.rdtypes.ANY.NS',
            'dns.rdtypes.ANY.SOA',
            'dns.rdtypes.ANY.TXT',
            'dns.rdtypes.IN',
            'dns.rdtypes.IN.A',
            'dns.rdtypes.IN.AAAA',
            'dns.name',
            'dns.message',
            'dns.query',
            'dns.rdata',
            'dns.rrset',
            # excel
            'xlrd',
            'xlwt',
            # tkinter
            'tkinter',
            'tkinter.ttk',
            'tkinter.filedialog',
            'tkinter.messagebox',
            'tkinter.scrolledtext',
            # stdlib
            'threading',
            'concurrent.futures',
            'smtplib',
            'socket',
            'ssl',
            'csv',
            'json',
            'logging',
            'datetime',
            'collections',
            'functools',
            'pathlib',
            'io',
            'os',
            're',
        ]
    ),

    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],

    excludes=[
        # trim heavy unused packages to keep EXE lean
        'matplotlib',
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
        'flask',
        'flask_cors',
        'werkzeug',
        'jinja2',
        'test',
        'unittest',
        'pydoc',
        'doctest',
        'setuptools',
        'pip',
    ],

    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PowerEmailValidation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        # never UPX-compress numpy/pandas DLLs — breaks them
        'numpy',
        'pandas',
        'libopenblas*',
        '*.pyd',
        '*.dll',
    ],
    runtime_tmpdir=None,
    console=False,           # no black console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',     # Power.png converted to ICO
)
