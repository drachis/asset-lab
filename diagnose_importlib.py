import sys, importlib
print("EXE:", sys.executable)
print("VER:", sys.version.replace('\n', ' '))
print("IMPORTLIB_FILE:", getattr(importlib, "__file__", None))
print("HAS_UTIL:", hasattr(importlib, "util"))
try:
    import importlib.util as _u
    print("UTIL_FILE:", getattr(_u, "__file__", None))
    print("PYGLTFLIB_SPEC:", _u.find_spec("pygltflib"))
except Exception as e:
    print("UTIL_ERROR:", repr(e))
print("SYS_PATH:", sys.path)
