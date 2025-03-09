# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

datas = []
datas += copy_metadata('packaging')
datas += copy_metadata('paddlepaddle')
datas += copy_metadata('requests')
datas += copy_metadata('numpy')


block_cipher = None


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[('C:/Users/vinat/miniconda3/envs/standalone_app_diffir/lib/site-packages/onnxruntime/capi/onnxruntime_providers_cuda.dll', './onnxruntime/capi/'), ('C:/Users/vinat/miniconda3/envs/standalone_app_diffir/Lib/site-packages/paddle/libs/*.dll', './paddle/libs/'), ('C:/Users/vinat/miniconda3/envs/standalone_app_diffir/lib/site-packages/onnxruntime/capi/onnxruntime_providers_tensorrt.dll', './onnxruntime/capi/')],
    datas=datas,
    hiddenimports=['numpy', 'numpy.core._dtype_ctypes', 'sklearn.utils._cython_blas', 'sklearn.neighbors.typedefs', 'sklearn.neighbors.quad_tree', 'sklearn.tree', 'imgaug', 'lmdb', 'sklearn.tree._utils', 'scipy.special._ufuncs', 'scipy.special._ufuncs_cxx', 'scipy.special._special_ufuncs', 'scipy.special._ellip_harm_2', 'scipy._lib.array_api_compat.numpy.fft', 'pyclipper', 'Polygon3', 'Polygon', 'requests', 'lanms', 'numpy.distutils', 'paddle', 'paddleocr', 'paddle.fluid', 'paddle.dataset'],
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='app',
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
    icon=['icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app',
)
