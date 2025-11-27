#!/usr/bin/env python3
"""
Quick test script to verify ConanX installation.
Run this after installing the package to ensure everything works.
"""

import sys
import subprocess

def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Command: {cmd}")
    print('='*60)

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print(f"✓ SUCCESS")
            if result.stdout:
                print("\nOutput:")
                print(result.stdout[:500])  # Print first 500 chars
        else:
            print(f"✗ FAILED (exit code: {result.returncode})")
            if result.stderr:
                print("\nError:")
                print(result.stderr[:500])

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("✗ FAILED (timeout)")
        return False
    except Exception as e:
        print(f"✗ FAILED (exception: {e})")
        return False

def test_import():
    """Test if package can be imported."""
    print(f"\n{'='*60}")
    print("Testing: Python import")
    print('='*60)

    try:
        import conanx
        print(f"✓ SUCCESS - conanx imported successfully")
        print(f"  Version: {conanx.__version__}")
        print(f"  Author: {conanx.__author__}")
        return True
    except ImportError as e:
        print(f"✗ FAILED - Cannot import conanx: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("ConanX Installation Test Suite")
    print("="*60)

    results = []

    # Test 1: Python import
    results.append(("Python import", test_import()))

    # Test 2: CLI executable exists
    results.append(("CLI help command", run_command("conanx --help", "CLI help command")))

    # Test 3: Test init command help
    results.append(("Init command", run_command("conanx init --help", "Init command help")))

    # Test 4: Test setup command help
    results.append(("Setup command", run_command("conanx setup --help", "Setup command help")))

    # Test 5: Test create command help
    results.append(("Create command", run_command("conanx create --help", "Create command help")))

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {name}")

    print("-"*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)

    if passed == total:
        print("\n✓ All tests passed! ConanX is installed correctly.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
