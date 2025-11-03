#!/usr/bin/env python3
"""
Test script to verify production fixes work correctly.

Tests the enhanced error handling and fallback mechanisms.
"""

import os
import tempfile
import shutil
import sys
from unittest.mock import patch

def test_fallback_directory_creation():
    """Test that fallback directory creation works."""
    print("🧪 Testing fallback directory creation...")

    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a subdirectory that's read-only
        readonly_dir = os.path.join(temp_dir, "readonly")
        os.makedirs(readonly_dir)
        os.chmod(readonly_dir, 0o444)  # Read-only

        try:
            # Test DataManager with read-only primary location
            with patch('data_manager.DataManager._ensure_directories') as mock_ensure:
                mock_ensure.side_effect = Exception("Permission denied")

                from data_manager import DataManager

                # This should trigger fallback logic
                dm = DataManager(base_path=readonly_dir)

                print("   ✅ DataManager handled directory creation failure gracefully")
                print(f"   📁 Final base path: {dm.base_path}")

                return True

        except Exception as e:
            print(f"   ❌ Fallback test failed: {e}")
            return False

def test_module_import_fallbacks():
    """Test that module imports have proper fallbacks."""
    print("\n🧪 Testing module import fallbacks...")

    try:
        # Test BBC scraper import with data_manager failure
        with patch.dict('sys.modules', {'data_manager': None}):
            # Force reimport by removing from cache if present
            modules_to_remove = [mod for mod in sys.modules if mod.startswith('bbc_scraper')]
            for mod in modules_to_remove:
                del sys.modules[mod]

            from bbc_scraper import BBCSportScraper

            print("   ✅ BBC scraper imported successfully with fallback data_manager")
            return True

    except Exception as e:
        print(f"   ❌ Module import fallback test failed: {e}")
        return False

def test_enhanced_health_check():
    """Test the enhanced health check endpoint."""
    print("\n🧪 Testing enhanced health check...")

    try:
        from app import app

        with app.test_client() as client:
            response = client.get('/health')
            data = response.get_json()

            print(f"   ✅ Health check responded with status: {data.get('status')}")
            print(f"   📊 Services status: {data.get('services', {})}")
            print(f"   💾 Filesystem status: {data.get('filesystem', {})}")

            # Check if enhanced fields are present
            required_fields = ['environment', 'filesystem', 'data_manager_errors', 'working_directory']
            for field in required_fields:
                if field in data:
                    print(f"   ✅ Enhanced field present: {field}")
                else:
                    print(f"   ❌ Missing enhanced field: {field}")
                    return False

            return True

    except Exception as e:
        print(f"   ❌ Health check test failed: {e}")
        return False

def test_admin_route_error_handling():
    """Test admin route error handling improvements."""
    print("\n🧪 Testing admin route error handling...")

    try:
        from app import app

        with app.test_client() as client:
            # Test with data_manager disabled
            with patch('app.data_manager', None):
                response = client.get('/admin')

                print(f"   📊 Response status: {response.status_code}")

                if response.status_code == 500:
                    response_text = response.get_data(as_text=True)

                    # Check if enhanced error message is present
                    if "filesystem permissions" in response_text.lower():
                        print("   ✅ Enhanced error message present in response")
                        return True
                    else:
                        print("   ❌ Enhanced error message not found in response")
                        return False
                else:
                    print(f"   ⚠️ Expected 500 status, got {response.status_code}")
                    return False

    except Exception as e:
        print(f"   ❌ Admin route error handling test failed: {e}")
        return False

def main():
    """Run all production fix tests."""
    print("🔧 TESTING PRODUCTION FIXES")
    print("=" * 50)

    tests = [
        test_fallback_directory_creation,
        test_module_import_fallbacks,
        test_enhanced_health_check,
        test_admin_route_error_handling
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Test {test.__name__} crashed: {e}")
            results.append(False)

    print("\n📊 TEST SUMMARY")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1}. {test.__name__}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All production fixes are working correctly!")
        return True
    else:
        print("⚠️ Some tests failed - fixes may need adjustment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)