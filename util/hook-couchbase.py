import os
import glob
import itertools

try:
    # PY_EXTENSION_SUFFIXES is unavailable in older versions
    from PyInstaller.hooks.hookutils import PY_EXTENSION_SUFFIXES
except ImportError:
    try:
        from importlib.machinery import EXTENSION_SUFFIXES as PY_EXTENSION_SUFFIXES
    except ImportError:
        import imp
        PY_EXTENSION_SUFFIXES = set([f[0] for f in imp.get_suffixes()
                                     if f[2] == imp.C_EXTENSION])

def hook(mod):
    module_directory = os.path.dirname(mod.__file__)
    bundled = []

    for libname, ext in itertools.product(('libcouchbase', '_libcouchbase'),
                                          PY_EXTENSION_SUFFIXES):
        bundled.extend(glob.glob(os.path.join(module_directory, libname + ext)))

    for f in bundled:
        name = os.path.join('couchbase', os.path.basename(f))
        if hasattr(mod, 'pyinstaller_binaries'):
            mod.pyinstaller_binaries.append((name, f, 'BINARY'))
        else: # mod.pyinstaller_binaries is unavailable in older versions
            mod.binaries.append((name, f, 'BINARY'))

    return mod