#!/usr/bin/env python3
"""
Performance comparison between AWS S3 (BulkBoto3) and Azure Blob Storage (BulkAzureBlob).
This test compares upload and download performance between the two cloud storage solutions.
"""

import asyncio
import os
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import csv
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the modules to test
from cloudbulkupload import BulkBoto3, BulkAzureBlob, StorageTransferPath

# Test configuration
TEST_CONFIG = {
    "file_sizes": [1024, 10240, 102400, 1048576],  # 1KB, 10KB, 100KB, 1MB
    "file_counts": [10, 50, 100],
    "concurrent_operations": [10, 25, 50],
    "iterations": 3,
    "test_dir": "performance_test_files",
    "results_file": "performance_comparison_results.csv"
}


class PerformanceTester:
    """Class to handle performance testing for both AWS S3 and Azure Blob Storage."""
    
    def __init__(self):
        """Initialize the performance tester with configuration."""
        self.results = []
        self.test_dir = Path(TEST_CONFIG["test_dir"])
        
        # AWS S3 configuration
        self.aws_endpoint = os.getenv("AWS_ENDPOINT_URL", "http://localhost:9000")
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        
        # Azure configuration
        self.azure_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        
        # Test buckets/containers
        self.aws_bucket = "performance-test-aws"
        self.azure_container = "performance-test-azure"
        
        # Initialize clients
        self.aws_client = None
        self.azure_client = None
        
        if self.aws_access_key and self.aws_secret_key:
            self.aws_client = BulkBoto3(
                endpoint_url=self.aws_endpoint,
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                max_pool_connections=50,
                verbose=False
            )
        
        if self.azure_connection_string:
            self.azure_client = BulkAzureBlob(
                connection_string=self.azure_connection_string,
                max_concurrent_operations=50,
                verbose=False
            )
    
    def create_test_files(self, file_size: int, file_count: int) -> List[str]:
        """Create test files with specified size and count."""
        files = []
        self.test_dir.mkdir(exist_ok=True)
        
        for i in range(file_count):
            file_path = self.test_dir / f"test_file_{file_size}_{i}.bin"
            with open(file_path, "wb") as f:
                f.write(os.urandom(file_size))
            files.append(str(file_path))
        
        return files
    
    def cleanup_test_files(self):
        """Clean up test files and directories."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    async def test_azure_upload(self, files: List[str], concurrent_ops: int) -> Dict:
        """Test Azure Blob Storage upload performance."""
        if not self.azure_client:
            return {"error": "Azure client not configured"}
        
        # Create upload paths
        upload_paths = [
            StorageTransferPath(
                local_path=file_path,
                storage_path=f"test/{os.path.basename(file_path)}"
            )
            for file_path in files
        ]
        
        # Measure upload time
        start_time = time.time()
        total_size = sum(os.path.getsize(f) for f in files)
        
        try:
            await self.azure_client.upload_files(
                container_name=self.azure_container,
                upload_paths=upload_paths
            )
            
            elapsed_time = time.time() - start_time
            speed = total_size / (1024 * 1024 * elapsed_time) if elapsed_time > 0 else 0
            
            return {
                "platform": "Azure Blob Storage",
                "operation": "upload",
                "file_count": len(files),
                "total_size_mb": total_size / (1024 * 1024),
                "elapsed_time": elapsed_time,
                "speed_mbps": speed,
                "concurrent_ops": concurrent_ops,
                "status": "success"
            }
        except Exception as e:
            return {
                "platform": "Azure Blob Storage",
                "operation": "upload",
                "file_count": len(files),
                "total_size_mb": total_size / (1024 * 1024),
                "elapsed_time": time.time() - start_time,
                "speed_mbps": 0,
                "concurrent_ops": concurrent_ops,
                "status": "error",
                "error": str(e)
            }
    
    def test_aws_upload(self, files: List[str], concurrent_ops: int) -> Dict:
        """Test AWS S3 upload performance."""
        if not self.aws_client:
            return {"error": "AWS client not configured"}
        
        # Create upload paths
        upload_paths = [
            StorageTransferPath(
                local_path=file_path,
                storage_path=f"test/{os.path.basename(file_path)}"
            )
            for file_path in files
        ]
        
        # Measure upload time
        start_time = time.time()
        total_size = sum(os.path.getsize(f) for f in files)
        
        try:
            self.aws_client.upload(
                bucket_name=self.aws_bucket,
                upload_paths=upload_paths
            )
            
            elapsed_time = time.time() - start_time
            speed = total_size / (1024 * 1024 * elapsed_time) if elapsed_time > 0 else 0
            
            return {
                "platform": "AWS S3",
                "operation": "upload",
                "file_count": len(files),
                "total_size_mb": total_size / (1024 * 1024),
                "elapsed_time": elapsed_time,
                "speed_mbps": speed,
                "concurrent_ops": concurrent_ops,
                "status": "success"
            }
        except Exception as e:
            return {
                "platform": "AWS S3",
                "operation": "upload",
                "file_count": len(files),
                "total_size_mb": total_size / (1024 * 1024),
                "elapsed_time": time.time() - start_time,
                "speed_mbps": 0,
                "concurrent_ops": concurrent_ops,
                "status": "error",
                "error": str(e)
            }
    
    async def test_azure_download(self, files: List[str], concurrent_ops: int) -> Dict:
        """Test Azure Blob Storage download performance."""
        if not self.azure_client:
            return {"error": "Azure client not configured"}
        
        # Create download paths
        download_dir = self.test_dir / "download_azure"
        download_dir.mkdir(exist_ok=True)
        
        download_paths = [
            StorageTransferPath(
                local_path=str(download_dir / os.path.basename(file_path)),
                storage_path=f"test/{os.path.basename(file_path)}"
            )
            for file_path in files
        ]
        
        # Measure download time
        start_time = time.time()
        total_size = sum(os.path.getsize(f) for f in files)
        
        try:
            await self.azure_client.download_files(
                container_name=self.azure_container,
                download_paths=download_paths
            )
            
            elapsed_time = time.time() - start_time
            speed = total_size / (1024 * 1024 * elapsed_time) if elapsed_time > 0 else 0
            
            return {
                "platform": "Azure Blob Storage",
                "operation": "download",
                "file_count": len(files),
                "total_size_mb": total_size / (1024 * 1024),
                "elapsed_time": elapsed_time,
                "speed_mbps": speed,
                "concurrent_ops": concurrent_ops,
                "status": "success"
            }
        except Exception as e:
            return {
                "platform": "Azure Blob Storage",
                "operation": "download",
                "file_count": len(files),
                "total_size_mb": total_size / (1024 * 1024),
                "elapsed_time": time.time() - start_time,
                "speed_mbps": 0,
                "concurrent_ops": concurrent_ops,
                "status": "error",
                "error": str(e)
            }
    
    def test_aws_download(self, files: List[str], concurrent_ops: int) -> Dict:
        """Test AWS S3 download performance."""
        if not self.aws_client:
            return {"error": "AWS client not configured"}
        
        # Create download paths
        download_dir = self.test_dir / "download_aws"
        download_dir.mkdir(exist_ok=True)
        
        download_paths = [
            StorageTransferPath(
                local_path=str(download_dir / os.path.basename(file_path)),
                storage_path=f"test/{os.path.basename(file_path)}"
            )
            for file_path in files
        ]
        
        # Measure download time
        start_time = time.time()
        total_size = sum(os.path.getsize(f) for f in files)
        
        try:
            self.aws_client.download(
                bucket_name=self.aws_bucket,
                download_paths=download_paths
            )
            
            elapsed_time = time.time() - start_time
            speed = total_size / (1024 * 1024 * elapsed_time) if elapsed_time > 0 else 0
            
            return {
                "platform": "AWS S3",
                "operation": "download",
                "file_count": len(files),
                "total_size_mb": total_size / (1024 * 1024),
                "elapsed_time": elapsed_time,
                "speed_mbps": speed,
                "concurrent_ops": concurrent_ops,
                "status": "success"
            }
        except Exception as e:
            return {
                "platform": "AWS S3",
                "operation": "download",
                "file_count": len(files),
                "total_size_mb": total_size / (1024 * 1024),
                "elapsed_time": time.time() - start_time,
                "speed_mbps": 0,
                "concurrent_ops": concurrent_ops,
                "status": "error",
                "error": str(e)
            }
    
    async def setup_storage(self):
        """Set up storage buckets/containers for testing."""
        print("🔧 Setting up storage for testing...")
        
        if self.aws_client:
            try:
                self.aws_client.create_new_bucket(self.aws_bucket)
                print(f"✅ Created AWS S3 bucket: {self.aws_bucket}")
            except Exception as e:
                print(f"⚠️  AWS bucket setup: {e}")
        
        if self.azure_client:
            try:
                await self.azure_client.create_container(self.azure_container)
                print(f"✅ Created Azure container: {self.azure_container}")
            except Exception as e:
                print(f"⚠️  Azure container setup: {e}")
    
    async def cleanup_storage(self):
        """Clean up storage buckets/containers after testing."""
        print("🧹 Cleaning up storage...")
        
        if self.aws_client:
            try:
                self.aws_client.empty_bucket(self.aws_bucket)
                print(f"✅ Emptied AWS S3 bucket: {self.aws_bucket}")
            except Exception as e:
                print(f"⚠️  AWS cleanup: {e}")
        
        if self.azure_client:
            try:
                await self.azure_client.empty_container(self.azure_container)
                print(f"✅ Emptied Azure container: {self.azure_container}")
            except Exception as e:
                print(f"⚠️  Azure cleanup: {e}")
    
    async def run_performance_tests(self):
        """Run comprehensive performance tests."""
        print("🚀 Starting Performance Comparison Tests")
        print("=" * 60)
        
        await self.setup_storage()
        
        for file_size in TEST_CONFIG["file_sizes"]:
            for file_count in TEST_CONFIG["file_counts"]:
                for concurrent_ops in TEST_CONFIG["concurrent_operations"]:
                    print(f"\n📁 Testing: {file_count} files of {file_size} bytes each, {concurrent_ops} concurrent operations")
                    
                    # Create test files
                    files = self.create_test_files(file_size, file_count)
                    
                    # Run multiple iterations
                    for iteration in range(TEST_CONFIG["iterations"]):
                        print(f"  Iteration {iteration + 1}/{TEST_CONFIG['iterations']}")
                        
                        # Test uploads
                        if self.aws_client:
                            aws_upload_result = self.test_aws_upload(files, concurrent_ops)
                            aws_upload_result.update({
                                "file_size": file_size,
                                "iteration": iteration + 1
                            })
                            self.results.append(aws_upload_result)
                        
                        if self.azure_client:
                            azure_upload_result = await self.test_azure_upload(files, concurrent_ops)
                            azure_upload_result.update({
                                "file_size": file_size,
                                "iteration": iteration + 1
                            })
                            self.results.append(azure_upload_result)
                        
                        # Test downloads (only if uploads were successful)
                        if self.aws_client and aws_upload_result.get("status") == "success":
                            aws_download_result = self.test_aws_download(files, concurrent_ops)
                            aws_download_result.update({
                                "file_size": file_size,
                                "iteration": iteration + 1
                            })
                            self.results.append(aws_download_result)
                        
                        if self.azure_client and azure_upload_result.get("status") == "success":
                            azure_download_result = await self.test_azure_download(files, concurrent_ops)
                            azure_download_result.update({
                                "file_size": file_size,
                                "iteration": iteration + 1
                            })
                            self.results.append(azure_download_result)
                    
                    # Clean up test files
                    self.cleanup_test_files()
        
        await self.cleanup_storage()
        
        # Save results
        self.save_results()
        self.print_summary()
    
    def save_results(self):
        """Save test results to CSV file."""
        if not self.results:
            print("⚠️  No results to save")
            return
        
        with open(TEST_CONFIG["results_file"], "w", newline="") as csvfile:
            fieldnames = [
                "platform", "operation", "file_count", "file_size", "total_size_mb",
                "elapsed_time", "speed_mbps", "concurrent_ops", "iteration", "status"
            ]
            
            # Add error field if any results have errors
            if any("error" in result for result in self.results):
                fieldnames.append("error")
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.results:
                writer.writerow(result)
        
        print(f"✅ Results saved to {TEST_CONFIG['results_file']}")
    
    def print_summary(self):
        """Print a summary of the test results."""
        print("\n📊 Performance Test Summary")
        print("=" * 60)
        
        if not self.results:
            print("No results to display")
            return
        
        # Group results by platform and operation
        summary = {}
        for result in self.results:
            if result.get("status") != "success":
                continue
            
            key = (result["platform"], result["operation"])
            if key not in summary:
                summary[key] = []
            summary[key].append(result)
        
        # Calculate averages
        for (platform, operation), results in summary.items():
            avg_speed = sum(r["speed_mbps"] for r in results) / len(results)
            avg_time = sum(r["elapsed_time"] for r in results) / len(results)
            total_files = sum(r["file_count"] for r in results)
            total_size = sum(r["total_size_mb"] for r in results)
            
            print(f"\n{platform} - {operation.title()}:")
            print(f"  Average Speed: {avg_speed:.2f} MB/s")
            print(f"  Average Time: {avg_time:.2f} seconds")
            print(f"  Total Files: {total_files}")
            print(f"  Total Size: {total_size:.2f} MB")
        
        # Compare platforms
        print("\n🏆 Performance Comparison:")
        for operation in ["upload", "download"]:
            aws_results = [r for r in self.results if r.get("platform") == "AWS S3" and r.get("operation") == operation and r.get("status") == "success"]
            azure_results = [r for r in self.results if r.get("platform") == "Azure Blob Storage" and r.get("operation") == operation and r.get("status") == "success"]
            
            if aws_results and azure_results:
                aws_avg_speed = sum(r["speed_mbps"] for r in aws_results) / len(aws_results)
                azure_avg_speed = sum(r["speed_mbps"] for r in azure_results) / len(azure_results)
                
                winner = "AWS S3" if aws_avg_speed > azure_avg_speed else "Azure Blob Storage"
                speed_diff = abs(aws_avg_speed - azure_avg_speed)
                
                print(f"  {operation.title()}: {winner} wins by {speed_diff:.2f} MB/s")


async def main():
    """Main function to run performance tests."""
    tester = PerformanceTester()
    
    # Check if clients are configured
    if not tester.aws_client and not tester.azure_client:
        print("❌ Error: No cloud storage clients configured")
        print("Please set the following environment variables:")
        print("  - AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY for AWS S3")
        print("  - AZURE_STORAGE_CONNECTION_STRING for Azure Blob Storage")
        return
    
    if not tester.aws_client:
        print("⚠️  AWS S3 client not configured, skipping AWS tests")
    
    if not tester.azure_client:
        print("⚠️  Azure Blob Storage client not configured, skipping Azure tests")
    
    try:
        await tester.run_performance_tests()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
    finally:
        tester.cleanup_test_files()


if __name__ == "__main__":
    asyncio.run(main())
