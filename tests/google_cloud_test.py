#!/usr/bin/env python3
"""
Google Cloud Storage Test Suite for cloudbulkupload

This test suite tests the Google Cloud Storage functionality including:
- Basic operations (upload, download, list, delete)
- Performance testing with different file sizes and concurrency levels
- Comparison with Google's official transfer manager
- Error handling and edge cases
"""

import os
import sys
import time
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
import statistics

# Add the parent directory to the path to import cloudbulkupload
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from cloudbulkupload import BulkGoogleStorage, google_bulk_upload_blobs, google_bulk_download_blobs
from cloudbulkupload import StorageTransferPath

# Load environment variables
load_dotenv()

class GoogleCloudTester:
    """Test suite for Google Cloud Storage functionality"""
    
    def __init__(self):
        """Initialize the tester with Google Cloud credentials from environment"""
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        self.credentials_path = os.getenv("GOOGLE_CLOUD_CREDENTIALS_PATH")
        self.credentials_json = os.getenv("GOOGLE_CLOUD_CREDENTIALS_JSON")
        
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT_ID not found in environment")
        
        if not self.credentials_path and not self.credentials_json:
            raise ValueError("No Google Cloud credentials found in environment")
        
        # Initialize the client
        self.client = BulkGoogleStorage(
            project_id=self.project_id,
            credentials_path=self.credentials_path,
            credentials_json=self.credentials_json,
            max_concurrent_operations=50,
            verbose=False
        )
        
        # Test configuration
        self.test_bucket = "cloudbulkupload-test"
        self.results = []
        
    def create_test_files(self, num_files: int = 10, file_size_mb: int = 1) -> List[str]:
        """Create test files with specified size"""
        print(f"📁 Creating {num_files} test files of {file_size_mb}MB each...")
        
        test_files = []
        temp_dir = tempfile.mkdtemp()
        
        for i in range(num_files):
            filename = f"test_file_{i:03d}.txt"
            filepath = os.path.join(temp_dir, filename)
            
            # Create file with random content
            with open(filepath, 'w') as f:
                # Write file_size_mb MB of data
                chunk = "A" * 1024 * 1024  # 1MB chunk
                for _ in range(file_size_mb):
                    f.write(chunk)
            
            test_files.append(filepath)
        
        print(f"✅ Created {len(test_files)} test files in {temp_dir}")
        return test_files, temp_dir
    
    def create_upload_paths(self, file_paths: List[str]) -> List[StorageTransferPath]:
        """Convert file paths to StorageTransferPath objects"""
        upload_paths = []
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            upload_paths.append(StorageTransferPath(
                local_path=file_path,
                storage_path=f"test/{filename}"
            ))
        return upload_paths
    
    async def test_basic_operations(self) -> Dict[str, Any]:
        """Test basic Google Cloud Storage operations"""
        print("\n🔧 Testing Basic Operations")
        print("=" * 50)
        
        results = {
            "test_name": "basic_operations",
            "bucket_creation": False,
            "file_upload": False,
            "file_download": False,
            "file_listing": False,
            "file_deletion": False,
            "bucket_deletion": False,
            "errors": []
        }
        
        try:
            # Create bucket
            print("📦 Creating test bucket...")
            await self.client.create_bucket(self.test_bucket)
            results["bucket_creation"] = True
            print("✅ Bucket created successfully")
            
            # Create test files
            test_files, temp_dir = self.create_test_files(num_files=5, file_size_mb=1)
            
            # Convert to upload paths
            upload_paths = self.create_upload_paths(test_files)
            
            # Upload files
            print("⬆️  Uploading test files...")
            start_time = time.time()
            await self.client.upload_files(self.test_bucket, upload_paths)
            upload_time = time.time() - start_time
            results["file_upload"] = True
            print(f"✅ Files uploaded in {upload_time:.2f}s")
            
            # List files
            print("📋 Listing files...")
            blobs = await self.client.list_blobs(self.test_bucket)
            results["file_listing"] = True
            print(f"✅ Found {len(blobs)} files in bucket")
            
            # Download files
            print("⬇️  Downloading files...")
            download_dir = tempfile.mkdtemp()
            download_paths = []
            for blob_name in blobs:
                local_path = os.path.join(download_dir, os.path.basename(blob_name))
                download_paths.append(StorageTransferPath(
                    local_path=local_path,
                    storage_path=blob_name
                ))
            
            start_time = time.time()
            await self.client.download_files(self.test_bucket, download_paths)
            download_time = time.time() - start_time
            results["file_download"] = True
            print(f"✅ Files downloaded in {download_time:.2f}s")
            
            # Delete files (empty bucket)
            print("🗑️  Deleting files...")
            await self.client.empty_bucket(self.test_bucket)
            results["file_deletion"] = True
            print("✅ Files deleted successfully")
            
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
            shutil.rmtree(download_dir, ignore_errors=True)
            
            # Delete bucket
            print("🗑️  Deleting test bucket...")
            await self.client.delete_bucket(self.test_bucket)
            results["bucket_deletion"] = True
            print("✅ Bucket deleted successfully")
            
        except Exception as e:
            results["errors"].append(str(e))
            print(f"❌ Error in basic operations: {e}")
        
        return results
    
    async def test_performance_upload(self, num_files: int = 20, file_size_mb: int = 5) -> Dict[str, Any]:
        """Test upload performance with different configurations"""
        print(f"\n⚡ Testing Upload Performance ({num_files} files, {file_size_mb}MB each)")
        print("=" * 60)
        
        results = {
            "test_name": "performance_upload",
            "num_files": num_files,
            "file_size_mb": file_size_mb,
            "total_size_mb": num_files * file_size_mb,
            "concurrency_levels": [],
            "errors": []
        }
        
        try:
            # Create test bucket
            await self.client.create_bucket(self.test_bucket)
            
            # Create test files
            test_files, temp_dir = self.create_test_files(num_files, file_size_mb)
            
            # Test different concurrency levels
            concurrency_levels = [1, 5, 10, 20, 50]
            
            for concurrency in concurrency_levels:
                print(f"\n🔄 Testing with {concurrency} concurrent operations...")
                
                # Create client with specific concurrency
                test_client = BulkGoogleStorage(
                    project_id=self.project_id,
                    credentials_path=self.credentials_path,
                    credentials_json=self.credentials_json,
                    max_concurrent_operations=concurrency,
                    verbose=False
                )
                
                # Clear bucket first
                await test_client.empty_bucket(self.test_bucket)
                
                # Convert to upload paths
                upload_paths = self.create_upload_paths(test_files)
                
                # Upload with timing
                start_time = time.time()
                await test_client.upload_files(self.test_bucket, upload_paths)
                upload_time = time.time() - start_time
                
                # Calculate metrics
                total_size_mb = num_files * file_size_mb
                speed_mbps = total_size_mb / upload_time
                
                result = {
                    "concurrency": concurrency,
                    "upload_time": upload_time,
                    "speed_mbps": speed_mbps,
                    "files_per_second": num_files / upload_time
                }
                
                results["concurrency_levels"].append(result)
                
                print(f"   ⏱️  Upload time: {upload_time:.2f}s")
                print(f"   🚀 Speed: {speed_mbps:.2f} MB/s")
                print(f"   📁 Files/sec: {result['files_per_second']:.2f}")
            
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
            await self.client.delete_bucket(self.test_bucket)
            
        except Exception as e:
            results["errors"].append(str(e))
            print(f"❌ Error in performance test: {e}")
        
        return results
    
    async def test_transfer_manager_comparison(self, num_files: int = 20, file_size_mb: int = 5) -> Dict[str, Any]:
        """Compare our implementation with Google's transfer manager"""
        print(f"\n🔄 Comparing with Google Transfer Manager ({num_files} files, {file_size_mb}MB each)")
        print("=" * 70)
        
        results = {
            "test_name": "transfer_manager_comparison",
            "num_files": num_files,
            "file_size_mb": file_size_mb,
            "total_size_mb": num_files * file_size_mb,
            "cloudbulkupload_results": {},
            "transfer_manager_results": {},
            "errors": []
        }
        
        try:
            # Create test bucket
            await self.client.create_bucket(self.test_bucket)
            
            # Create test files
            test_files, temp_dir = self.create_test_files(num_files, file_size_mb)
            
            # Test our implementation
            print("🔄 Testing cloudbulkupload implementation...")
            upload_paths = self.create_upload_paths(test_files)
            
            start_time = time.time()
            await self.client.upload_files(self.test_bucket, upload_paths)
            our_time = time.time() - start_time
            
            results["cloudbulkupload_results"] = {
                "upload_time": our_time,
                "speed_mbps": (num_files * file_size_mb) / our_time,
                "files_per_second": num_files / our_time
            }
            
            print(f"   ⏱️  cloudbulkupload time: {our_time:.2f}s")
            print(f"   🚀 Speed: {results['cloudbulkupload_results']['speed_mbps']:.2f} MB/s")
            
            # Clear bucket
            await self.client.empty_bucket(self.test_bucket)
            
            # Test Google's transfer manager
            print("🔄 Testing Google Transfer Manager...")
            start_time = time.time()
            
            # Import Google's transfer manager
            from google.cloud.storage import Client, transfer_manager
            
            # Initialize client
            if self.credentials_json:
                import json
                from google.oauth2 import service_account
                credentials_info = json.loads(self.credentials_json)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_info, scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
                storage_client = Client(credentials=credentials, project=self.project_id)
            elif self.credentials_path:
                storage_client = Client.from_service_account_json(self.credentials_path, project=self.project_id)
            else:
                storage_client = Client(project=self.project_id)
            
            bucket = storage_client.bucket(self.test_bucket)
            
            # Get just filenames for transfer manager
            filenames = [os.path.basename(f) for f in test_files]
            source_directory = os.path.dirname(test_files[0])
            
            # Use transfer manager
            transfer_results = transfer_manager.upload_many_from_filenames(
                bucket, filenames, source_directory=source_directory, max_workers=50
            )
            
            # Check for errors
            errors = [r for r in transfer_results if isinstance(r, Exception)]
            if errors:
                raise Exception(f"Transfer manager errors: {errors}")
            
            transfer_time = time.time() - start_time
            
            results["transfer_manager_results"] = {
                "upload_time": transfer_time,
                "speed_mbps": (num_files * file_size_mb) / transfer_time,
                "files_per_second": num_files / transfer_time
            }
            
            print(f"   ⏱️  Transfer Manager time: {transfer_time:.2f}s")
            print(f"   🚀 Speed: {results['transfer_manager_results']['speed_mbps']:.2f} MB/s")
            
            # Compare results
            our_speed = results["cloudbulkupload_results"]["speed_mbps"]
            tm_speed = results["transfer_manager_results"]["speed_mbps"]
            
            if our_speed > tm_speed:
                improvement = ((our_speed - tm_speed) / tm_speed) * 100
                print(f"   🏆 cloudbulkupload is {improvement:.1f}% faster!")
            else:
                improvement = ((tm_speed - our_speed) / our_speed) * 100
                print(f"   🏆 Transfer Manager is {improvement:.1f}% faster!")
            
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
            await self.client.delete_bucket(self.test_bucket)
            
        except Exception as e:
            results["errors"].append(str(e))
            print(f"❌ Error in transfer manager comparison: {e}")
        
        return results
    
    async def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling scenarios"""
        print("\n🚨 Testing Error Handling")
        print("=" * 40)
        
        results = {
            "test_name": "error_handling",
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": []
        }
        
        try:
            # Test 1: Non-existent bucket
            print("🔍 Test 1: Non-existent bucket operations...")
            try:
                await self.client.list_blobs("non-existent-bucket-12345")
                print("   ❌ Should have failed for non-existent bucket")
                results["tests_failed"] += 1
            except Exception as e:
                print(f"   ✅ Correctly handled non-existent bucket: {type(e).__name__}")
                results["tests_passed"] += 1
            
            # Test 2: Invalid file paths
            print("🔍 Test 2: Invalid file paths...")
            try:
                invalid_paths = [StorageTransferPath(
                    local_path="/non/existent/file.txt",
                    storage_path="test/file.txt"
                )]
                await self.client.upload_files(self.test_bucket, invalid_paths)
                print("   ❌ Should have failed for invalid file path")
                results["tests_failed"] += 1
            except Exception as e:
                print(f"   ✅ Correctly handled invalid file path: {type(e).__name__}")
                results["tests_passed"] += 1
            
            # Test 3: Empty file list
            print("🔍 Test 3: Empty file list...")
            try:
                await self.client.upload_files(self.test_bucket, [])
                print("   ✅ Correctly handled empty file list")
                results["tests_passed"] += 1
            except Exception as e:
                print(f"   ❌ Should have handled empty file list gracefully: {e}")
                results["tests_failed"] += 1
            
        except Exception as e:
            results["errors"].append(str(e))
            print(f"❌ Error in error handling test: {e}")
        
        return results
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        print("🚀 Google Cloud Storage Test Suite")
        print("=" * 50)
        
        all_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "project_id": self.project_id,
            "tests": []
        }
        
        # Run basic operations test
        basic_results = await self.test_basic_operations()
        all_results["tests"].append(basic_results)
        
        # Run performance tests
        perf_results = await self.test_performance_upload(num_files=20, file_size_mb=5)
        all_results["tests"].append(perf_results)
        
        # Run transfer manager comparison
        comparison_results = await self.test_transfer_manager_comparison(num_files=20, file_size_mb=5)
        all_results["tests"].append(comparison_results)
        
        # Run error handling tests
        error_results = await self.test_error_handling()
        all_results["tests"].append(error_results)
        
        # Print summary
        print("\n📊 Test Summary")
        print("=" * 30)
        
        for test in all_results["tests"]:
            test_name = test["test_name"]
            if "errors" in test and test["errors"]:
                print(f"❌ {test_name}: {len(test['errors'])} errors")
            else:
                print(f"✅ {test_name}: Passed")
        
        return all_results

async def main():
    """Main test runner"""
    try:
        tester = GoogleCloudTester()
        results = await tester.run_all_tests()
        
        # Save results to file
        import json
        with open("google_cloud_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to google_cloud_test_results.json")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
