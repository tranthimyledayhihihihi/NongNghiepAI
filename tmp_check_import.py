import sys
import traceback

sys.path.insert(0, "backend")

try:
    import app.main  # noqa: F401
    print("IMPORT_OK")
except Exception as e:
    print("IMPORT_FAIL:", repr(e))
    traceback.print_exc()
