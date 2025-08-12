#!/usr/bin/env python3
"""
Test runner script for cloudbulkupload package.
This script provides easy ways to run different types of tests.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run tests for cloudbulkupload")
    parser.add_argument(
        "--type",
        choices=["unit", "performance", "all", "benchmark", "comparison", "quick", "azure-comparison", "three-way-comparison", "google-cloud"],
        default="unit",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage reporting"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--keep-data",
        action="store_true",
        help="Keep test data and buckets (don't cleanup)"
    )
    parser.add_argument(
        "--keep-buckets",
        action="store_true",
        help="Keep test buckets but clean up data"
    )
    parser.add_argument(
        "--keep-files",
        action="store_true",
        help="Keep local test files but clean up buckets"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Disable all cleanup operations"
    )
    
    args = parser.parse_args()
    
    # Set environment variables based on command line arguments
    if args.no_cleanup:
        import os
        os.environ["CLEANUP_ENABLED"] = "false"
    elif args.keep_data:
        import os
        os.environ["KEEP_TEST_DATA"] = "true"
        os.environ["KEEP_BUCKETS"] = "true"
    elif args.keep_buckets:
        import os
        os.environ["KEEP_BUCKETS"] = "true"
    elif args.keep_files:
        import os
        os.environ["KEEP_LOCAL_FILES"] = "true"
    
    # Check if we're in the right directory
    if not Path("tests").exists():
        print("❌ Error: tests directory not found. Please run from project root.")
        sys.exit(1)
    
    # Install test dependencies if needed
    print("📦 Installing test dependencies...")
    subprocess.run([
        sys.executable, "-m", "pip", "install", "-e", ".[test]"
    ], check=True)
    
    if args.type == "unit":
        # Run unit tests
        cmd = [sys.executable, "-m", "pytest", "tests/test_bulkboto3.py", "-m", "not slow"]
        if args.coverage:
            cmd.extend(["--cov=cloudbulkupload", "--cov-report=html", "--cov-report=term"])
        if args.verbose:
            cmd.append("-v")
        
        success = run_command(cmd, "Unit Tests")
        
    elif args.type == "performance":
        # Run performance tests
        cmd = [sys.executable, "-m", "pytest", "tests/test_bulkboto3.py", "-m", "performance"]
        if args.verbose:
            cmd.append("-v")
        
        success = run_command(cmd, "Performance Tests")
        
    elif args.type == "all":
        # Run all tests
        cmd = [sys.executable, "-m", "pytest", "tests/"]
        if args.coverage:
            cmd.extend(["--cov=cloudbulkupload", "--cov-report=html", "--cov-report=term"])
        if args.verbose:
            cmd.append("-v")
        
        success = run_command(cmd, "All Tests")
        
    elif args.type == "benchmark":
        # Run performance benchmark
        cmd = [sys.executable, "tests/performance_benchmark.py"]
        success = run_command(cmd, "Performance Benchmark")
        
    elif args.type == "comparison":
        # Run comparison tests
        cmd = [sys.executable, "tests/comparison_test.py"]
        success = run_command(cmd, "Comparison Tests")
        
    elif args.type == "azure-comparison":
        # Run Azure vs AWS performance comparison
        cmd = [sys.executable, "tests/performance_comparison.py"]
        success = run_command(cmd, "Azure vs AWS Performance Comparison")
        
    elif args.type == "three-way-comparison":
        # Run three-way performance comparison (AWS, Azure, Google)
        cmd = [sys.executable, "tests/performance_comparison_three_way.py"]
        success = run_command(cmd, "Three-Way Performance Comparison (AWS, Azure, Google)")
    
    elif args.type == "google-cloud":
        # Run Google Cloud Storage test suite
        cmd = [sys.executable, "tests/google_cloud_test.py"]
        success = run_command(cmd, "Google Cloud Storage Test Suite")
        
    elif args.type == "quick":
        # Run quick test
        cmd = [sys.executable, "tests/quick_test.py"]
        success = run_command(cmd, "Quick Test")
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
