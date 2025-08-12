#!/usr/bin/env python3
"""
Comparison test suite for cloudbulkupload vs regular boto3.
This script compares the performance of cloudbulkupload with standard boto3 uploads.
"""

import os
import time
import tempfile
import statistics
import csv
from pathlib import Path
from typing import Dict, List, Tuple
import unittest
import pytest

import boto3
from dotenv import load_dotenv

from cloudbulkupload import BulkBoto3, StorageTransferPath
try:
    from test_config import get_test_config
except ImportError:
    from tests.test_config import get_test_config

# Load environment variables
load_dotenv()


class TestComparison(unittest.TestCase):
    """Test suite comparing cloudbulkupload with regular boto3."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        # Load test configuration
        cls.config = get_test_config()
        cls.config.print_config()
        
        # Load AWS credentials from .env file
        cls.endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:9000")
        cls.access_key = os.getenv("AWS_ACCESS_KEY_ID")
        cls.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        
        if not cls.access_key or not cls.secret_key:
            raise ValueError("AWS credentials not found in .env file")
        
        # Initialize both clients
        cls.bulkboto = BulkBoto3(
            endpoint_url=cls.endpoint_url,
            aws_access_key_id=cls.access_key,
            aws_secret_access_key=cls.secret_key,
            max_pool_connections=cls.config.max_threads,
            verbose=cls.config.verbose_tests
        )
        
        cls.s3_client = boto3.client(
            's3',
            aws_access_key_id=cls.access_key,
            aws_secret_access_key=cls.secret_key,
            endpoint_url=cls.endpoint_url
        )
        
        # Create test buckets
        cls.bulkboto_bucket = "comparison-bulkboto-bucket"
        cls.boto3_bucket = "comparison-boto3-bucket"
        
        try:
            cls.bulkboto.create_new_bucket(cls.bulkboto_bucket)
        except:
            pass  # Bucket might already exist
        
        try:
            cls.s3_client.create_bucket(Bucket=cls.boto3_bucket)
        except:
            pass  # Bucket might already exist
        
        # Create test directory
        cls.test_dir = tempfile.mkdtemp(prefix="comparison_test_")
        cls.setup_test_files()
        
        # Results storage
        cls.results = []
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        # Clean up buckets based on configuration
        if cls.config.should_cleanup("buckets"):
            try:
                print(cls.config.get_cleanup_message("buckets"))
                cls.bulkboto.empty_bucket(cls.bulkboto_bucket)
                cls.bulkboto.resource.Bucket(cls.bulkboto_bucket).delete()
                cls.s3_client.delete_bucket(Bucket=cls.boto3_bucket)
                print("✅ Buckets cleanup completed")
            except Exception as e:
                print(f"⚠️  Warning: Could not clean up buckets: {e}")
        else:
            print(cls.config.get_cleanup_message("buckets"))
        
        # Clean up local files based on configuration
        if cls.config.should_cleanup("local_files"):
            try:
                print(cls.config.get_cleanup_message("local_files"))
                import shutil
                shutil.rmtree(cls.test_dir, ignore_errors=True)
                print("✅ Local files cleanup completed")
            except Exception as e:
                print(f"⚠️  Warning: Could not clean up local files: {e}")
        else:
            print(cls.config.get_cleanup_message("local_files"))
    
    @classmethod
    def setup_test_files(cls):
        """Create test files of various sizes."""
        print("Setting up test files for comparison...")
        
        # Create files of different sizes
        file_sizes = {
            "small": 1024,        # 1KB
            "medium": 1024 * 100,  # 100KB
            "large": 1024 * 1024,  # 1MB
            "xlarge": 5 * 1024 * 1024,  # 5MB
        }
        
        for size_name, size_bytes in file_sizes.items():
            file_path = Path(cls.test_dir) / f"{size_name}_file.txt"
            content = "A" * size_bytes
            file_path.write_text(content)
            print(f"Created {size_name} file: {size_bytes / 1024:.1f}KB")
        
        # Create multiple small files for bulk testing
        for i in range(20):
            file_path = Path(cls.test_dir) / f"bulk_file_{i:03d}.txt"
            content = f"This is bulk file {i} with some content for comparison testing"
            file_path.write_text(content)
        
        print(f"Created {len(list(Path(cls.test_dir).glob('*')))} test files")
    
    def setUp(self):
        """Set up before each test."""
        # Clear buckets before each test
        try:
            self.bulkboto.empty_bucket(self.bulkboto_bucket)
            self.s3_client.delete_objects(
                Bucket=self.boto3_bucket,
                Delete={'Objects': [{'Key': obj.key} for obj in self.bulkboto.resource.Bucket(self.boto3_bucket).objects.all()]}
            )
        except:
            pass
    
    @pytest.mark.comparison
    def test_single_file_upload_comparison(self):
        """Compare single file upload performance between cloudbulkupload and boto3."""
        print("\n" + "="*60)
        print("SINGLE FILE UPLOAD COMPARISON")
        print("="*60)
        
        file_sizes = ["small", "medium", "large", "xlarge"]
        results = []
        
        for size_name in file_sizes:
            file_path = Path(self.test_dir) / f"{size_name}_file.txt"
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            
            print(f"\nTesting {size_name} file ({file_size_mb:.2f}MB)...")
            
            # Test cloudbulkupload
            start_time = time.time()
            self.bulkboto.upload(
                bucket_name=self.bulkboto_bucket,
                upload_paths=StorageTransferPath(
                    local_path=str(file_path),
                    storage_path=f"bulkboto_{size_name}.txt"
                )
            )
            bulkboto_time = time.time() - start_time
            bulkboto_speed = file_size_mb / bulkboto_time if bulkboto_time > 0 else 0
            
            # Test regular boto3
            start_time = time.time()
            self.s3_client.upload_file(
                str(file_path),
                self.boto3_bucket,
                f"boto3_{size_name}.txt"
            )
            boto3_time = time.time() - start_time
            boto3_speed = file_size_mb / boto3_time if boto3_time > 0 else 0
            
            # Calculate improvement
            speedup = boto3_time / bulkboto_time if bulkboto_time > 0 else 0
            improvement = ((boto3_time - bulkboto_time) / boto3_time) * 100 if boto3_time > 0 else 0
            
            result = {
                "test_type": "single_file_upload",
                "file_size": size_name,
                "file_size_mb": file_size_mb,
                "bulkboto_time": bulkboto_time,
                "bulkboto_speed": bulkboto_speed,
                "boto3_time": boto3_time,
                "boto3_speed": boto3_speed,
                "speedup_factor": speedup,
                "improvement_percent": improvement
            }
            results.append(result)
            
            print(f"  cloudbulkupload: {bulkboto_time:.3f}s ({bulkboto_speed:.2f} MB/s)")
            print(f"  boto3:          {boto3_time:.3f}s ({boto3_speed:.2f} MB/s)")
            print(f"  Speedup:        {speedup:.2f}x ({improvement:.1f}% faster)")
        
        self.results.extend(results)
        return results
    
    @pytest.mark.comparison
    def test_directory_upload_comparison(self):
        """Compare directory upload performance between cloudbulkupload and boto3."""
        print("\n" + "="*60)
        print("DIRECTORY UPLOAD COMPARISON")
        print("="*60)
        
        thread_counts = [1, 5, 10]
        results = []
        
        for n_threads in thread_counts:
            print(f"\nTesting directory upload with {n_threads} threads...")
            
            # Calculate total size
            total_size = sum(f.stat().st_size for f in Path(self.test_dir).glob("*"))
            total_size_mb = total_size / (1024 * 1024)
            
            # Test cloudbulkupload
            start_time = time.time()
            self.bulkboto.upload_dir_to_storage(
                bucket_name=self.bulkboto_bucket,
                local_dir=self.test_dir,
                storage_dir=f"bulkboto_dir_{n_threads}",
                n_threads=n_threads
            )
            bulkboto_time = time.time() - start_time
            bulkboto_speed = total_size_mb / bulkboto_time if bulkboto_time > 0 else 0
            
            # Count uploaded objects
            bulkboto_objects = self.bulkboto.list_objects(
                bucket_name=self.bulkboto_bucket,
                storage_dir=f"bulkboto_dir_{n_threads}"
            )
            
            # Test regular boto3 (sequential)
            start_time = time.time()
            uploaded_count = 0
            for file_path in Path(self.test_dir).glob("*"):
                if file_path.is_file():
                    s3_key = f"boto3_dir_{n_threads}/{file_path.name}"
                    self.s3_client.upload_file(str(file_path), self.boto3_bucket, s3_key)
                    uploaded_count += 1
            boto3_time = time.time() - start_time
            boto3_speed = total_size_mb / boto3_time if boto3_time > 0 else 0
            
            # Calculate improvement
            speedup = boto3_time / bulkboto_time if bulkboto_time > 0 else 0
            improvement = ((boto3_time - bulkboto_time) / boto3_time) * 100 if boto3_time > 0 else 0
            
            result = {
                "test_type": "directory_upload",
                "threads": n_threads,
                "total_size_mb": total_size_mb,
                "file_count": len(bulkboto_objects),
                "bulkboto_time": bulkboto_time,
                "bulkboto_speed": bulkboto_speed,
                "boto3_time": boto3_time,
                "boto3_speed": boto3_speed,
                "speedup_factor": speedup,
                "improvement_percent": improvement
            }
            results.append(result)
            
            print(f"  cloudbulkupload: {bulkboto_time:.3f}s ({bulkboto_speed:.2f} MB/s, {len(bulkboto_objects)} files)")
            print(f"  boto3:          {boto3_time:.3f}s ({boto3_speed:.2f} MB/s, {uploaded_count} files)")
            print(f"  Speedup:        {speedup:.2f}x ({improvement:.1f}% faster)")
        
        self.results.extend(results)
        return results
    
    @pytest.mark.comparison
    def test_multiple_files_upload_comparison(self):
        """Compare multiple files upload performance."""
        print("\n" + "="*60)
        print("MULTIPLE FILES UPLOAD COMPARISON")
        print("="*60)
        
        # Select a subset of files for testing
        test_files = list(Path(self.test_dir).glob("bulk_file_*.txt"))[:10]
        total_size = sum(f.stat().st_size for f in test_files)
        total_size_mb = total_size / (1024 * 1024)
        
        print(f"Testing {len(test_files)} files ({total_size_mb:.2f}MB total)...")
        
        # Test cloudbulkupload
        upload_paths = [
            StorageTransferPath(
                local_path=str(f),
                storage_path=f"bulkboto_multi/{f.name}"
            ) for f in test_files
        ]
        
        start_time = time.time()
        self.bulkboto.upload(
            bucket_name=self.bulkboto_bucket,
            upload_paths=upload_paths
        )
        bulkboto_time = time.time() - start_time
        bulkboto_speed = total_size_mb / bulkboto_time if bulkboto_time > 0 else 0
        
        # Test regular boto3
        start_time = time.time()
        for file_path in test_files:
            s3_key = f"boto3_multi/{file_path.name}"
            self.s3_client.upload_file(str(file_path), self.boto3_bucket, s3_key)
        boto3_time = time.time() - start_time
        boto3_speed = total_size_mb / boto3_time if boto3_time > 0 else 0
        
        # Calculate improvement
        speedup = boto3_time / bulkboto_time if bulkboto_time > 0 else 0
        improvement = ((boto3_time - bulkboto_time) / boto3_time) * 100 if boto3_time > 0 else 0
        
        result = {
            "test_type": "multiple_files_upload",
            "file_count": len(test_files),
            "total_size_mb": total_size_mb,
            "bulkboto_time": bulkboto_time,
            "bulkboto_speed": bulkboto_speed,
            "boto3_time": boto3_time,
            "boto3_speed": boto3_speed,
            "speedup_factor": speedup,
            "improvement_percent": improvement
        }
        self.results.append(result)
        
        print(f"  cloudbulkupload: {bulkboto_time:.3f}s ({bulkboto_speed:.2f} MB/s)")
        print(f"  boto3:          {boto3_time:.3f}s ({boto3_speed:.2f} MB/s)")
        print(f"  Speedup:        {speedup:.2f}x ({improvement:.1f}% faster)")
        
        return result
    
    @pytest.mark.comparison
    def test_large_file_upload_comparison(self):
        """Compare large file upload performance."""
        print("\n" + "="*60)
        print("LARGE FILE UPLOAD COMPARISON")
        print("="*60)
        
        # Create a large test file (10MB)
        large_file = Path(self.test_dir) / "large_comparison_file.txt"
        large_content = "A" * 10 * 1024 * 1024  # 10MB
        large_file.write_text(large_content)
        
        file_size_mb = len(large_content) / (1024 * 1024)
        print(f"Testing large file ({file_size_mb:.1f}MB)...")
        
        # Test cloudbulkupload
        start_time = time.time()
        self.bulkboto.upload(
            bucket_name=self.bulkboto_bucket,
            upload_paths=StorageTransferPath(
                local_path=str(large_file),
                storage_path="bulkboto_large.txt"
            )
        )
        bulkboto_time = time.time() - start_time
        bulkboto_speed = file_size_mb / bulkboto_time if bulkboto_time > 0 else 0
        
        # Test regular boto3
        start_time = time.time()
        self.s3_client.upload_file(
            str(large_file),
            self.boto3_bucket,
            "boto3_large.txt"
        )
        boto3_time = time.time() - start_time
        boto3_speed = file_size_mb / boto3_time if boto3_time > 0 else 0
        
        # Calculate improvement
        speedup = boto3_time / bulkboto_time if bulkboto_time > 0 else 0
        improvement = ((boto3_time - bulkboto_time) / boto3_time) * 100 if boto3_time > 0 else 0
        
        result = {
            "test_type": "large_file_upload",
            "file_size_mb": file_size_mb,
            "bulkboto_time": bulkboto_time,
            "bulkboto_speed": bulkboto_speed,
            "boto3_time": boto3_time,
            "boto3_speed": boto3_speed,
            "speedup_factor": speedup,
            "improvement_percent": improvement
        }
        self.results.append(result)
        
        print(f"  cloudbulkupload: {bulkboto_time:.3f}s ({bulkboto_speed:.2f} MB/s)")
        print(f"  boto3:          {boto3_time:.3f}s ({boto3_speed:.2f} MB/s)")
        print(f"  Speedup:        {speedup:.2f}x ({improvement:.1f}% faster)")
        
        return result
    
    @pytest.mark.comparison
    def test_error_handling_comparison(self):
        """Compare error handling between cloudbulkupload and boto3."""
        print("\n" + "="*60)
        print("ERROR HANDLING COMPARISON")
        print("="*60)
        
        # Test with non-existent file
        non_existent_file = "non_existent_file.txt"
        
        # Test cloudbulkupload error handling
        try:
            self.bulkboto.upload(
                bucket_name=self.bulkboto_bucket,
                upload_paths=StorageTransferPath(
                    local_path=non_existent_file,
                    storage_path="test.txt"
                )
            )
            bulkboto_error_handled = False
        except Exception as e:
            bulkboto_error_handled = True
            bulkboto_error_type = type(e).__name__
        
        # Test boto3 error handling
        try:
            self.s3_client.upload_file(non_existent_file, self.boto3_bucket, "test.txt")
            boto3_error_handled = False
        except Exception as e:
            boto3_error_handled = True
            boto3_error_type = type(e).__name__
        
        result = {
            "test_type": "error_handling",
            "bulkboto_error_handled": bulkboto_error_handled,
            "bulkboto_error_type": bulkboto_error_type if bulkboto_error_handled else "None",
            "boto3_error_handled": boto3_error_handled,
            "boto3_error_type": boto3_error_type if boto3_error_handled else "None"
        }
        self.results.append(result)
        
        print(f"  cloudbulkupload error handling: {'✅' if bulkboto_error_handled else '❌'}")
        print(f"  boto3 error handling: {'✅' if boto3_error_handled else '❌'}")
        
        return result
    
    def generate_comparison_report(self):
        """Generate a comprehensive comparison report."""
        print("\n" + "="*80)
        print("COMPARISON TEST REPORT")
        print("="*80)
        
        # Calculate overall statistics
        speedup_factors = [r["speedup_factor"] for r in self.results if "speedup_factor" in r]
        improvement_percentages = [r["improvement_percent"] for r in self.results if "improvement_percent" in r]
        
        if speedup_factors:
            avg_speedup = statistics.mean(speedup_factors)
            max_speedup = max(speedup_factors)
            min_speedup = min(speedup_factors)
            
            avg_improvement = statistics.mean(improvement_percentages)
            max_improvement = max(improvement_percentages)
            min_improvement = min(improvement_percentages)
            
            print(f"\nOVERALL PERFORMANCE SUMMARY:")
            print(f"  Average speedup: {avg_speedup:.2f}x")
            print(f"  Maximum speedup: {max_speedup:.2f}x")
            print(f"  Minimum speedup: {min_speedup:.2f}x")
            print(f"  Average improvement: {avg_improvement:.1f}%")
            print(f"  Maximum improvement: {max_improvement:.1f}%")
            print(f"  Minimum improvement: {min_improvement:.1f}%")
        
        # Detailed results by test type
        test_types = set(r["test_type"] for r in self.results)
        
        for test_type in test_types:
            type_results = [r for r in self.results if r["test_type"] == test_type]
            if type_results and "speedup_factor" in type_results[0]:
                type_speedups = [r["speedup_factor"] for r in type_results]
                type_improvements = [r["improvement_percent"] for r in type_results]
                
                print(f"\n{test_type.upper().replace('_', ' ')}:")
                print(f"  Average speedup: {statistics.mean(type_speedups):.2f}x")
                print(f"  Average improvement: {statistics.mean(type_improvements):.1f}%")
        
        # Recommendations
        print(f"\nRECOMMENDATIONS:")
        if speedup_factors and avg_speedup > 1.5:
            print(f"  ✅ cloudbulkupload shows significant performance improvement")
        elif speedup_factors and avg_speedup > 1.1:
            print(f"  ⚠️  cloudbulkupload shows moderate performance improvement")
        else:
            print(f"  ❌ cloudbulkupload performance improvement is minimal")
        
        if speedup_factors and max_speedup > 5:
            print(f"  🚀 Excellent performance for specific use cases")
        
        return self.results


def run_comparison_tests():
    """Run all comparison tests and generate report."""
    # Create test instance
    test_instance = TestComparison()
    test_instance.setUpClass()
    
    try:
        # Run all comparison tests
        test_instance.test_single_file_upload_comparison()
        test_instance.test_directory_upload_comparison()
        test_instance.test_multiple_files_upload_comparison()
        test_instance.test_large_file_upload_comparison()
        test_instance.test_error_handling_comparison()
        
        # Generate report
        results = test_instance.generate_comparison_report()
        
        # Save results to CSV
        save_results_to_csv(results, "test_results.csv")
        
        return results
        
    finally:
        test_instance.tearDownClass()


def save_results_to_csv(results, filename):
    """Save test results to CSV file."""
    if not results:
        return
    
    # Get all possible fieldnames from all results
    all_fieldnames = set()
    for result in results:
        all_fieldnames.update(result.keys())
    
    fieldnames = sorted(list(all_fieldnames))
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            # Fill missing fields with empty values
            row = {field: result.get(field, '') for field in fieldnames}
            writer.writerow(row)
    
    print(f"\nResults saved to {filename}")


if __name__ == "__main__":
    run_comparison_tests()
