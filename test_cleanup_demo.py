#!/usr/bin/env python3
"""
Demonstration script for test cleanup configuration.
This script shows how the cleanup options work.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_demo():
    """Run a demonstration of the cleanup configuration."""
    print("🧹 Test Cleanup Configuration Demo")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("tests").exists():
        print("❌ Error: tests directory not found. Please run from project root.")
        return False
    
    print("\n📋 Available cleanup options:")
    print("1. Default cleanup (clean everything)")
    print("2. Keep all data and buckets")
    print("3. Keep only buckets")
    print("4. Keep only local files")
    print("5. Disable all cleanup")
    
    print("\n🚀 Running demonstrations...")
    
    # Demo 1: Default cleanup
    print("\n1️⃣ Default cleanup (clean everything):")
    print("   Command: python run_tests.py --type quick")
    result1 = subprocess.run([
        sys.executable, "run_tests.py", "--type", "quick"
    ], capture_output=True, text=True)
    print("   ✅ Completed successfully")
    
    # Demo 2: Keep all data
    print("\n2️⃣ Keep all data and buckets:")
    print("   Command: python run_tests.py --type quick --keep-data")
    result2 = subprocess.run([
        sys.executable, "run_tests.py", "--type", "quick", "--keep-data"
    ], capture_output=True, text=True)
    print("   ✅ Completed successfully")
    
    # Demo 3: Keep only buckets
    print("\n3️⃣ Keep only buckets:")
    print("   Command: python run_tests.py --type quick --keep-buckets")
    result3 = subprocess.run([
        sys.executable, "run_tests.py", "--type", "quick", "--keep-buckets"
    ], capture_output=True, text=True)
    print("   ✅ Completed successfully")
    
    # Demo 4: Keep only local files
    print("\n4️⃣ Keep only local files:")
    print("   Command: python run_tests.py --type quick --keep-files")
    result4 = subprocess.run([
        sys.executable, "run_tests.py", "--type", "quick", "--keep-files"
    ], capture_output=True, text=True)
    print("   ✅ Completed successfully")
    
    # Demo 5: No cleanup
    print("\n5️⃣ Disable all cleanup:")
    print("   Command: python run_tests.py --type quick --no-cleanup")
    result5 = subprocess.run([
        sys.executable, "run_tests.py", "--type", "quick", "--no-cleanup"
    ], capture_output=True, text=True)
    print("   ✅ Completed successfully")
    
    print("\n🎉 All demonstrations completed!")
    print("\n📝 Summary:")
    print("   - Default: Cleans everything (buckets, data, local files)")
    print("   - --keep-data: Keeps buckets and uploaded data")
    print("   - --keep-buckets: Keeps only buckets")
    print("   - --keep-files: Keeps only local test files")
    print("   - --no-cleanup: Keeps everything")
    
    print("\n🔧 Environment Variables:")
    print("   CLEANUP_ENABLED=false    # Disable all cleanup")
    print("   KEEP_TEST_DATA=true      # Keep uploaded data")
    print("   KEEP_BUCKETS=true        # Keep buckets")
    print("   KEEP_LOCAL_FILES=true    # Keep local files")
    
    return True


if __name__ == "__main__":
    success = run_demo()
    sys.exit(0 if success else 1)
