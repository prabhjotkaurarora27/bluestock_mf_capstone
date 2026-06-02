"""
test_environment.py
--------------------
Environment verification script for Bluestock MF Capstone.
Run this script to confirm all required packages are correctly installed.
"""

import sys

print("=" * 55)
print("  Bluestock MF Capstone — Environment Test")
print("=" * 55)
print(f"  Python version : {sys.version}")
print("=" * 55)

# Track pass/fail
results = []

def test_import(package_name, import_name=None, attr="__version__"):
    """Try importing a package and print its version."""
    import_name = import_name or package_name
    try:
        module = __import__(import_name)
        version = getattr(module, attr, "version unknown")
        print(f"  ✅  {package_name:<15} v{version}")
        results.append((package_name, True))
    except ImportError as e:
        print(f"  ❌  {package_name:<15} FAILED — {e}")
        results.append((package_name, False))

print("\n  Checking packages:\n")
test_import("pandas")
test_import("numpy")
test_import("matplotlib")
test_import("seaborn")
test_import("plotly")
test_import("sqlalchemy", "sqlalchemy")
test_import("requests")
test_import("scipy")
test_import("jupyter", "jupyter_core")

# Summary
passed = sum(1 for _, ok in results if ok)
failed = sum(1 for _, ok in results if not ok)

print("\n" + "=" * 55)
print(f"  Result : {passed} passed  |  {failed} failed")
print("=" * 55)

if failed == 0:
    print("\n  🎉 All packages imported successfully!")
    print("  Your environment is ready for the capstone project.\n")
else:
    failed_pkgs = [name for name, ok in results if not ok]
    print(f"\n  ⚠️  Please reinstall: {', '.join(failed_pkgs)}\n")
    sys.exit(1)
