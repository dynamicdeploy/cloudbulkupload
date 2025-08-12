#!/usr/bin/env python3
"""
Three-Way Performance Comparison Test Suite

This test suite compares the performance of:
1. AWS S3 (cloudbulkupload)
2. Azure Blob Storage (cloudbulkupload)
3. Google Cloud Storage (cloudbulkupload)
4. Google Cloud Storage (Google's Transfer Manager)

The tests measure upload and download performance across different scenarios.
"""

import os
import sys
import time
import asyncio
import tempfile
import shutil
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import statistics

# Add the parent directory to the path to import cloudbulkupload
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from cloudbulkupload import (
    BulkBoto3, 
    BulkAzureBlob, 
    BulkGoogleStorage,
    StorageTransferPath,
    bulk_upload_blobs as azure_bulk_upload,
    bulk_download_blobs as azure_bulk_download,
    google_bulk_upload_blobs,
    google_bulk_download_blobs
)

# Load environment variables
load_dotenv()

class ThreeWayPerformanceTester:
    """Comprehensive performance tester for AWS, Azure, and Google Cloud"""
    
    def __init__(self):
        """Initialize all cloud clients"""
        # AWS Configuration
        self.aws_endpoint = os.getenv("AWS_ENDPOINT_URL")
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_bucket = os.getenv("DEFAULT_BUCKET", "test-bucket")
        
        # Azure Configuration
        self.azure_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.azure_container = "test-container"
        
        # Google Cloud Configuration
        self.google_project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        self.google_credentials_path = os.getenv("GOOGLE_CLOUD_CREDENTIALS_PATH")
        self.google_credentials_json = os.getenv("GOOGLE_CLOUD_CREDENTIALS_JSON")
        self.google_bucket = "cloudbulkupload-performance-test"
        
        # Initialize clients
        self.aws_client = None
        self.azure_client = None
        self.google_client = None
        
        self._initialize_clients()
        
        # Test configuration
        self.results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_scenarios": [],
            "summary": {}
        }
    
    def _initialize_clients(self):
        """Initialize cloud clients based on available credentials"""
        print("🔧 Initializing Cloud Clients...")
        
        # Initialize AWS client
        if self.aws_access_key and self.aws_secret_key:
            try:
                self.aws_client = BulkBoto3(
                    aws_access_key_id=self.aws_access_key,
                    aws_secret_access_key=self.aws_secret_key,
                    endpoint_url=self.aws_endpoint,
                    max_pool_connections=300,
                    verbose=False
                )
                print("✅ AWS S3 client initialized")
            except Exception as e:
                print(f"❌ Failed to initialize AWS client: {e}")
        
        # Initialize Azure client
        if self.azure_connection_string:
            try:
                self.azure_client = BulkAzureBlob(
                    connection_string=self.azure_connection_string,
                    max_concurrent_operations=50,
                    verbose=False
                )
                print("✅ Azure Blob Storage client initialized")
            except Exception as e:
                print(f"❌ Failed to initialize Azure client: {e}")
        
        # Initialize Google Cloud client
        if self.google_project_id and (self.google_credentials_path or self.google_credentials_json):
            try:
                self.google_client = BulkGoogleStorage(
                    project_id=self.google_project_id,
                    credentials_path=self.google_credentials_path,
                    credentials_json=self.google_credentials_json,
                    max_concurrent_operations=50,
                    verbose=False
                )
                print("✅ Google Cloud Storage client initialized")
            except Exception as e:
                print(f"❌ Failed to initialize Google Cloud client: {e}")
    
    def create_test_files(self, num_files: int = 20, file_size_mb: int = 5) -> tuple:
        """Create test files with specified parameters"""
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
    
    def create_upload_paths(self, file_paths: List[str], provider: str) -> List[StorageTransferPath]:
        """Convert file paths to StorageTransferPath objects"""
        upload_paths = []
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            upload_paths.append(StorageTransferPath(
                local_path=file_path,
                storage_path=f"test/{filename}"
            ))
        return upload_paths
    
    async def test_aws_performance(self, test_files: List[str], scenario_name: str) -> Dict[str, Any]:
        """Test AWS S3 performance"""
        if not self.aws_client:
            return {"error": "AWS client not available"}
        
        print(f"\n☁️  Testing AWS S3 Performance: {scenario_name}")
        print("-" * 50)
        
        results = {
            "provider": "AWS S3",
            "scenario": scenario_name,
            "upload_time": None,
            "download_time": None,
            "upload_speed_mbps": None,
            "download_speed_mbps": None,
            "files_per_second": None,
            "errors": []
        }
        
        try:
            # Create bucket if needed
            try:
                await self.aws_client.create_bucket(self.aws_bucket)
            except:
                pass  # Bucket might already exist
            
            # Upload test
            print("⬆️  Uploading files to AWS S3...")
            start_time = time.time()
            await self.aws_client.upload_files(self.aws_bucket, test_files)
            upload_time = time.time() - start_time
            
            total_size_mb = len(test_files) * 5  # Assuming 5MB per file
            upload_speed = total_size_mb / upload_time
            
            results.update({
                "upload_time": upload_time,
                "upload_speed_mbps": upload_speed,
                "files_per_second": len(test_files) / upload_time
            })
            
            print(f"   ⏱️  Upload time: {upload_time:.2f}s")
            print(f"   🚀 Upload speed: {upload_speed:.2f} MB/s")
            
            # Download test
            print("⬇️  Downloading files from AWS S3...")
            download_dir = tempfile.mkdtemp()
            start_time = time.time()
            await self.aws_client.download_files(self.aws_bucket, download_dir)
            download_time = time.time() - start_time
            
            download_speed = total_size_mb / download_time
            
            results.update({
                "download_time": download_time,
                "download_speed_mbps": download_speed
            })
            
            print(f"   ⏱️  Download time: {download_time:.2f}s")
            print(f"   🚀 Download speed: {download_speed:.2f} MB/s")
            
            # Cleanup
            shutil.rmtree(download_dir, ignore_errors=True)
            await self.aws_client.delete_files(self.aws_bucket)
            
        except Exception as e:
            results["errors"].append(str(e))
            print(f"❌ AWS S3 test failed: {e}")
        
        return results
    
    async def test_azure_performance(self, test_files: List[str], scenario_name: str) -> Dict[str, Any]:
        """Test Azure Blob Storage performance"""
        if not self.azure_client:
            return {"error": "Azure client not available"}
        
        print(f"\n🔷 Testing Azure Blob Storage Performance: {scenario_name}")
        print("-" * 50)
        
        results = {
            "provider": "Azure Blob Storage",
            "scenario": scenario_name,
            "upload_time": None,
            "download_time": None,
            "upload_speed_mbps": None,
            "download_speed_mbps": None,
            "files_per_second": None,
            "errors": []
        }
        
        try:
            # Create container if needed
            try:
                await self.azure_client.create_container(self.azure_container)
            except:
                pass  # Container might already exist
            
            # Upload test
            print("⬆️  Uploading files to Azure Blob Storage...")
            upload_paths = self.create_upload_paths(test_files, "azure")
            start_time = time.time()
            await self.azure_client.upload_files(self.azure_container, upload_paths)
            upload_time = time.time() - start_time
            
            total_size_mb = len(test_files) * 5  # Assuming 5MB per file
            upload_speed = total_size_mb / upload_time
            
            results.update({
                "upload_time": upload_time,
                "upload_speed_mbps": upload_speed,
                "files_per_second": len(test_files) / upload_time
            })
            
            print(f"   ⏱️  Upload time: {upload_time:.2f}s")
            print(f"   🚀 Upload speed: {upload_speed:.2f} MB/s")
            
            # Download test
            print("⬇️  Downloading files from Azure Blob Storage...")
            download_dir = tempfile.mkdtemp()
            start_time = time.time()
            await self.azure_client.download_files(self.azure_container, download_dir)
            download_time = time.time() - start_time
            
            download_speed = total_size_mb / download_time
            
            results.update({
                "download_time": download_time,
                "download_speed_mbps": download_speed
            })
            
            print(f"   ⏱️  Download time: {download_time:.2f}s")
            print(f"   🚀 Download speed: {download_speed:.2f} MB/s")
            
            # Cleanup
            shutil.rmtree(download_dir, ignore_errors=True)
            await self.azure_client.delete_files(self.azure_container)
            
        except Exception as e:
            results["errors"].append(str(e))
            print(f"❌ Azure Blob Storage test failed: {e}")
        
        return results
    
    async def test_google_performance(self, test_files: List[str], scenario_name: str) -> Dict[str, Any]:
        """Test Google Cloud Storage performance"""
        if not self.google_client:
            return {"error": "Google Cloud client not available"}
        
        print(f"\n🔶 Testing Google Cloud Storage Performance: {scenario_name}")
        print("-" * 50)
        
        results = {
            "provider": "Google Cloud Storage",
            "scenario": scenario_name,
            "upload_time": None,
            "download_time": None,
            "upload_speed_mbps": None,
            "download_speed_mbps": None,
            "files_per_second": None,
            "errors": []
        }
        
        try:
            # Create bucket if needed
            try:
                await self.google_client.create_bucket(self.google_bucket)
            except:
                pass  # Bucket might already exist
            
            # Upload test
            print("⬆️  Uploading files to Google Cloud Storage...")
            upload_paths = self.create_upload_paths(test_files, "google")
            start_time = time.time()
            await self.google_client.upload_files(self.google_bucket, upload_paths)
            upload_time = time.time() - start_time
            
            total_size_mb = len(test_files) * 5  # Assuming 5MB per file
            upload_speed = total_size_mb / upload_time
            
            results.update({
                "upload_time": upload_time,
                "upload_speed_mbps": upload_speed,
                "files_per_second": len(test_files) / upload_time
            })
            
            print(f"   ⏱️  Upload time: {upload_time:.2f}s")
            print(f"   🚀 Upload speed: {upload_speed:.2f} MB/s")
            
            # Download test
            print("⬇️  Downloading files from Google Cloud Storage...")
            download_dir = tempfile.mkdtemp()
            start_time = time.time()
            await self.google_client.download_files(self.google_bucket, download_dir)
            download_time = time.time() - start_time
            
            download_speed = total_size_mb / download_time
            
            results.update({
                "download_time": download_time,
                "download_speed_mbps": download_speed
            })
            
            print(f"   ⏱️  Download time: {download_time:.2f}s")
            print(f"   🚀 Download speed: {download_speed:.2f} MB/s")
            
            # Cleanup
            shutil.rmtree(download_dir, ignore_errors=True)
            await self.google_client.delete_files(self.google_bucket)
            
        except Exception as e:
            results["errors"].append(str(e))
            print(f"❌ Google Cloud Storage test failed: {e}")
        
        return results
    
    async def test_google_transfer_manager(self, test_files: List[str], scenario_name: str) -> Dict[str, Any]:
        """Test Google's Transfer Manager performance"""
        if not self.google_project_id:
            return {"error": "Google Cloud credentials not available"}
        
        print(f"\n🔶 Testing Google Transfer Manager Performance: {scenario_name}")
        print("-" * 50)
        
        results = {
            "provider": "Google Transfer Manager",
            "scenario": scenario_name,
            "upload_time": None,
            "upload_speed_mbps": None,
            "files_per_second": None,
            "errors": []
        }
        
        try:
            # Import Google's transfer manager
            from google.cloud.storage import Client, transfer_manager
            
            # Initialize client
            if self.google_credentials_json:
                import json
                from google.oauth2 import service_account
                credentials_info = json.loads(self.google_credentials_json)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_info, scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
                storage_client = Client(credentials=credentials, project=self.google_project_id)
            elif self.google_credentials_path:
                storage_client = Client.from_service_account_json(self.google_credentials_path, project=self.google_project_id)
            else:
                storage_client = Client(project=self.google_project_id)
            
            bucket = storage_client.bucket(self.google_bucket)
            
            # Create bucket if needed
            try:
                bucket.create()
            except:
                pass  # Bucket might already exist
            
            # Get filenames for transfer manager
            filenames = [os.path.basename(f) for f in test_files]
            source_directory = os.path.dirname(test_files[0])
            
            # Upload test with transfer manager
            print("⬆️  Uploading files with Google Transfer Manager...")
            start_time = time.time()
            
            transfer_results = transfer_manager.upload_many_from_filenames(
                bucket, filenames, source_directory=source_directory, max_workers=50
            )
            
            # Check for errors
            errors = [r for r in transfer_results if isinstance(r, Exception)]
            if errors:
                raise Exception(f"Transfer manager errors: {errors}")
            
            upload_time = time.time() - start_time
            
            total_size_mb = len(test_files) * 5  # Assuming 5MB per file
            upload_speed = total_size_mb / upload_time
            
            results.update({
                "upload_time": upload_time,
                "upload_speed_mbps": upload_speed,
                "files_per_second": len(test_files) / upload_time
            })
            
            print(f"   ⏱️  Upload time: {upload_time:.2f}s")
            print(f"   🚀 Upload speed: {upload_speed:.2f} MB/s")
            
            # Cleanup
            for blob in bucket.list_blobs():
                blob.delete()
            
        except Exception as e:
            results["errors"].append(str(e))
            print(f"❌ Google Transfer Manager test failed: {e}")
        
        return results
    
    async def run_performance_scenario(self, num_files: int, file_size_mb: int, scenario_name: str):
        """Run a complete performance scenario across all providers"""
        print(f"\n🚀 Running Performance Scenario: {scenario_name}")
        print(f"📊 Configuration: {num_files} files, {file_size_mb}MB each")
        print("=" * 70)
        
        # Create test files
        test_files, temp_dir = self.create_test_files(num_files, file_size_mb)
        
        scenario_results = {
            "scenario_name": scenario_name,
            "num_files": num_files,
            "file_size_mb": file_size_mb,
            "total_size_mb": num_files * file_size_mb,
            "providers": []
        }
        
        try:
            # Test AWS S3
            aws_results = await self.test_aws_performance(test_files, scenario_name)
            scenario_results["providers"].append(aws_results)
            
            # Test Azure Blob Storage
            azure_results = await self.test_azure_performance(test_files, scenario_name)
            scenario_results["providers"].append(azure_results)
            
            # Test Google Cloud Storage
            google_results = await self.test_google_performance(test_files, scenario_name)
            scenario_results["providers"].append(google_results)
            
            # Test Google Transfer Manager
            transfer_results = await self.test_google_transfer_manager(test_files, scenario_name)
            scenario_results["providers"].append(transfer_results)
            
            # Print comparison
            self._print_scenario_comparison(scenario_results)
            
        finally:
            # Cleanup test files
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        return scenario_results
    
    def _print_scenario_comparison(self, scenario_results: Dict[str, Any]):
        """Print a comparison table for the scenario results"""
        print(f"\n📊 Performance Comparison: {scenario_results['scenario_name']}")
        print("=" * 80)
        print(f"{'Provider':<25} {'Upload Speed':<15} {'Download Speed':<15} {'Files/sec':<10}")
        print("-" * 80)
        
        for provider in scenario_results["providers"]:
            if "error" in provider:
                print(f"{provider['provider']:<25} {'ERROR':<15} {'ERROR':<15} {'ERROR':<10}")
                continue
            
            upload_speed = f"{provider.get('upload_speed_mbps', 0):.2f} MB/s"
            download_speed = f"{provider.get('download_speed_mbps', 0):.2f} MB/s"
            files_per_sec = f"{provider.get('files_per_second', 0):.2f}"
            
            print(f"{provider['provider']:<25} {upload_speed:<15} {download_speed:<15} {files_per_sec:<10}")
        
        # Find fastest upload
        valid_providers = [p for p in scenario_results["providers"] if "error" not in p and p.get("upload_speed_mbps")]
        if valid_providers:
            fastest = max(valid_providers, key=lambda x: x.get("upload_speed_mbps", 0))
            print(f"\n🏆 Fastest Upload: {fastest['provider']} ({fastest['upload_speed_mbps']:.2f} MB/s)")
    
    async def run_all_scenarios(self):
        """Run all performance scenarios"""
        print("🚀 Three-Way Performance Comparison Test Suite")
        print("=" * 60)
        
        scenarios = [
            {"num_files": 10, "file_size_mb": 1, "name": "Small Files (10x1MB)"},
            {"num_files": 20, "file_size_mb": 5, "name": "Medium Files (20x5MB)"},
            {"num_files": 50, "file_size_mb": 10, "name": "Large Files (50x10MB)"},
        ]
        
        for scenario in scenarios:
            scenario_results = await self.run_performance_scenario(
                scenario["num_files"], 
                scenario["file_size_mb"], 
                scenario["name"]
            )
            self.results["test_scenarios"].append(scenario_results)
        
        # Generate summary
        self._generate_summary()
        
        return self.results
    
    def _generate_summary(self):
        """Generate a summary of all test results"""
        print("\n📈 Overall Performance Summary")
        print("=" * 50)
        
        summary = {
            "total_scenarios": len(self.results["test_scenarios"]),
            "provider_performance": {},
            "best_performers": {}
        }
        
        # Collect all results by provider
        provider_results = {}
        
        for scenario in self.results["test_scenarios"]:
            for provider in scenario["providers"]:
                if "error" in provider:
                    continue
                
                provider_name = provider["provider"]
                if provider_name not in provider_results:
                    provider_results[provider_name] = []
                
                provider_results[provider_name].append(provider)
        
        # Calculate averages for each provider
        for provider_name, results in provider_results.items():
            upload_speeds = [r.get("upload_speed_mbps", 0) for r in results if r.get("upload_speed_mbps")]
            download_speeds = [r.get("download_speed_mbps", 0) for r in results if r.get("download_speed_mbps")]
            
            summary["provider_performance"][provider_name] = {
                "avg_upload_speed": statistics.mean(upload_speeds) if upload_speeds else 0,
                "avg_download_speed": statistics.mean(download_speeds) if download_speeds else 0,
                "max_upload_speed": max(upload_speeds) if upload_speeds else 0,
                "max_download_speed": max(download_speeds) if download_speeds else 0,
                "total_tests": len(results)
            }
        
        # Find best performers
        if summary["provider_performance"]:
            best_upload = max(summary["provider_performance"].items(), 
                            key=lambda x: x[1]["avg_upload_speed"])
            best_download = max(summary["provider_performance"].items(), 
                              key=lambda x: x[1]["avg_download_speed"])
            
            summary["best_performers"] = {
                "fastest_upload": best_upload[0],
                "fastest_download": best_download[0]
            }
        
        self.results["summary"] = summary
        
        # Print summary
        print(f"{'Provider':<25} {'Avg Upload':<15} {'Avg Download':<15} {'Tests':<10}")
        print("-" * 70)
        
        for provider, perf in summary["provider_performance"].items():
            avg_upload = f"{perf['avg_upload_speed']:.2f} MB/s"
            avg_download = f"{perf['avg_download_speed']:.2f} MB/s"
            tests = str(perf['total_tests'])
            
            print(f"{provider:<25} {avg_upload:<15} {avg_download:<15} {tests:<10}")
        
        if summary["best_performers"]:
            print(f"\n🏆 Fastest Upload: {summary['best_performers']['fastest_upload']}")
            print(f"🏆 Fastest Download: {summary['best_performers']['fastest_download']}")

async def main():
    """Main test runner"""
    try:
        tester = ThreeWayPerformanceTester()
        results = await tester.run_all_scenarios()
        
        # Save results to file
        with open("three_way_performance_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to three_way_performance_results.json")
        
        # Generate CSV report
        generate_csv_report(results)
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        sys.exit(1)

def generate_csv_report(results: Dict[str, Any]):
    """Generate a CSV report from the test results"""
    import csv
    
    csv_file = "three_way_performance_results.csv"
    
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow([
            'Scenario', 'Provider', 'Num Files', 'File Size (MB)', 'Total Size (MB)',
            'Upload Time (s)', 'Upload Speed (MB/s)', 'Download Time (s)', 'Download Speed (MB/s)',
            'Files per Second', 'Errors'
        ])
        
        # Write data
        for scenario in results["test_scenarios"]:
            for provider in scenario["providers"]:
                writer.writerow([
                    scenario["scenario_name"],
                    provider.get("provider", "Unknown"),
                    scenario["num_files"],
                    scenario["file_size_mb"],
                    scenario["total_size_mb"],
                    provider.get("upload_time", ""),
                    provider.get("upload_speed_mbps", ""),
                    provider.get("download_time", ""),
                    provider.get("download_speed_mbps", ""),
                    provider.get("files_per_second", ""),
                    "; ".join(provider.get("errors", []))
                ])
    
    print(f"📊 CSV report saved to {csv_file}")

if __name__ == "__main__":
    asyncio.run(main())
