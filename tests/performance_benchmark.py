#!/usr/bin/env python3
"""
Performance benchmarking script for cloudbulkupload package.
This script provides detailed performance analysis for upload operations.
"""

import os
import time
import statistics
from pathlib import Path
from typing import Dict, List, Tuple
import tempfile
import shutil

from dotenv import load_dotenv
from cloudbulkupload import BulkBoto3, StorageTransferPath
try:
    from test_config import get_test_config
except ImportError:
    from tests.test_config import get_test_config

# Load environment variables
load_dotenv()


class PerformanceBenchmark:
    """Performance benchmarking class for BulkBoto3."""
    
    def __init__(self):
        """Initialize the benchmark with AWS credentials."""
        # Load test configuration
        self.config = get_test_config()
        self.config.print_config()
        
        self.endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:9000")
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.bucket_name = "performance-benchmark-bucket"
        
        if not self.access_key or not self.secret_key:
            raise ValueError("AWS credentials not found in .env file")
        
        self.bulkboto = BulkBoto3(
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            max_pool_connections=self.config.max_threads,
            verbose=self.config.verbose_tests
        )
        
        # Create test bucket
        self.bulkboto.create_new_bucket(self.bucket_name)
        
        # Create test directory
        self.test_dir = tempfile.mkdtemp(prefix="performance_benchmark_")
        self.setup_test_files()
    
    def __del__(self):
        """Clean up resources."""
        # Clean up bucket based on configuration
        if self.config.should_cleanup("buckets"):
            try:
                print(self.config.get_cleanup_message("buckets"))
                self.bulkboto.empty_bucket(self.bucket_name)
                self.bulkboto.resource.Bucket(self.bucket_name).delete()
                print("✅ Bucket cleanup completed")
            except:
                pass
        
        # Clean up local files based on configuration
        if self.config.should_cleanup("local_files"):
            try:
                print(self.config.get_cleanup_message("local_files"))
                shutil.rmtree(self.test_dir, ignore_errors=True)
                print("✅ Local files cleanup completed")
            except:
                pass
    
    def setup_test_files(self):
        """Create test files of various sizes."""
        print("Setting up test files...")
        
        # Create files of different sizes
        file_sizes = {
            "small": 1024,        # 1KB
            "medium": 1024 * 100,  # 100KB
            "large": 1024 * 1024,  # 1MB
            "xlarge": 10 * 1024 * 1024,  # 10MB
        }
        
        for size_name, size_bytes in file_sizes.items():
            file_path = Path(self.test_dir) / f"{size_name}_file.txt"
            content = "A" * size_bytes
            file_path.write_text(content)
            print(f"Created {size_name} file: {size_bytes / 1024:.1f}KB")
        
        # Create multiple small files for bulk testing
        for i in range(50):
            file_path = Path(self.test_dir) / f"bulk_file_{i:03d}.txt"
            content = f"This is bulk file {i} with some content"
            file_path.write_text(content)
        
        print(f"Created {len(list(Path(self.test_dir).glob('*')))} test files")
    
    def measure_upload_performance(self, file_path: Path, storage_path: str, 
                                 iterations: int = 3) -> Dict:
        """Measure upload performance for a single file."""
        times = []
        file_size = file_path.stat().st_size
        
        for i in range(iterations):
            # Clear bucket before each test
            self.bulkboto.empty_bucket(self.bucket_name)
            
            start_time = time.time()
            self.bulkboto.upload(
                bucket_name=self.bucket_name,
                upload_paths=StorageTransferPath(
                    local_path=str(file_path),
                    storage_path=storage_path
                )
            )
            upload_time = time.time() - start_time
            times.append(upload_time)
            
            # Verify upload
            exists = self.bulkboto.check_object_exists(
                bucket_name=self.bucket_name,
                object_path=storage_path
            )
            if not exists:
                raise Exception(f"Upload verification failed for {file_path}")
        
        # Calculate statistics
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        
        # Calculate speed in MB/s
        speed_mbps = (file_size / (1024 * 1024)) / avg_time
        
        return {
            "file_size_bytes": file_size,
            "file_size_mb": file_size / (1024 * 1024),
            "times": times,
            "avg_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "std_dev": std_dev,
            "speed_mbps": speed_mbps
        }
    
    def benchmark_single_files(self) -> Dict:
        """Benchmark single file uploads of different sizes."""
        print("\n" + "="*60)
        print("SINGLE FILE UPLOAD BENCHMARK")
        print("="*60)
        
        results = {}
        
        for file_path in Path(self.test_dir).glob("*_file.txt"):
            size_name = file_path.stem.split('_')[0]
            print(f"\nTesting {size_name} file upload...")
            
            result = self.measure_upload_performance(
                file_path, f"single_{size_name}.txt"
            )
            results[size_name] = result
            
            print(f"  File size: {result['file_size_mb']:.2f}MB")
            print(f"  Average time: {result['avg_time']:.3f}s")
            print(f"  Speed: {result['speed_mbps']:.2f} MB/s")
            print(f"  Min/Max: {result['min_time']:.3f}s / {result['max_time']:.3f}s")
        
        return results
    
    def benchmark_directory_uploads(self) -> Dict:
        """Benchmark directory uploads with different thread counts."""
        print("\n" + "="*60)
        print("DIRECTORY UPLOAD BENCHMARK")
        print("="*60)
        
        thread_counts = [1, 2, 5, 10, 20, 50]
        results = {}
        
        for n_threads in thread_counts:
            print(f"\nTesting directory upload with {n_threads} threads...")
            
            # Clear bucket
            self.bulkboto.empty_bucket(self.bucket_name)
            
            start_time = time.time()
            self.bulkboto.upload_dir_to_storage(
                bucket_name=self.bucket_name,
                local_dir=self.test_dir,
                storage_dir=f"dir_test_{n_threads}",
                n_threads=n_threads
            )
            upload_time = time.time() - start_time
            
            # Count uploaded objects
            objects = self.bulkboto.list_objects(
                bucket_name=self.bucket_name,
                storage_dir=f"dir_test_{n_threads}"
            )
            
            # Calculate total size
            total_size = 0
            for obj in objects:
                try:
                    obj_info = self.bulkboto.resource.Object(self.bucket_name, obj).get()
                    total_size += obj_info['ContentLength']
                except:
                    pass
            
            speed_mbps = (total_size / (1024 * 1024)) / upload_time if upload_time > 0 else 0
            
            results[n_threads] = {
                "upload_time": upload_time,
                "object_count": len(objects),
                "total_size_mb": total_size / (1024 * 1024),
                "speed_mbps": speed_mbps
            }
            
            print(f"  Upload time: {upload_time:.3f}s")
            print(f"  Objects uploaded: {len(objects)}")
            print(f"  Total size: {total_size / (1024 * 1024):.2f}MB")
            print(f"  Speed: {speed_mbps:.2f} MB/s")
        
        return results
    
    def benchmark_concurrent_uploads(self) -> Dict:
        """Benchmark concurrent upload operations."""
        print("\n" + "="*60)
        print("CONCURRENT UPLOAD BENCHMARK")
        print("="*60)
        
        import threading
        import queue
        
        def upload_worker(file_queue, results_queue, worker_id):
            """Worker function for concurrent uploads."""
            while True:
                try:
                    file_path, storage_path = file_queue.get_nowait()
                except queue.Empty:
                    break
                
                start_time = time.time()
                try:
                    self.bulkboto.upload(
                        bucket_name=self.bucket_name,
                        upload_paths=StorageTransferPath(
                            local_path=str(file_path),
                            storage_path=storage_path
                        )
                    )
                    upload_time = time.time() - start_time
                    results_queue.put((worker_id, upload_time, True))
                except Exception as e:
                    results_queue.put((worker_id, 0, False))
                
                file_queue.task_done()
        
        # Test with different numbers of concurrent workers
        worker_counts = [1, 2, 5, 10]
        results = {}
        
        for n_workers in worker_counts:
            print(f"\nTesting {n_workers} concurrent upload workers...")
            
            # Clear bucket
            self.bulkboto.empty_bucket(self.bucket_name)
            
            # Prepare file queue
            file_queue = queue.Queue()
            results_queue = queue.Queue()
            
            # Add files to queue
            files = list(Path(self.test_dir).glob("bulk_file_*.txt"))
            for i, file_path in enumerate(files):
                storage_path = f"concurrent_{n_workers}/file_{i:03d}.txt"
                file_queue.put((file_path, storage_path))
            
            # Start workers
            start_time = time.time()
            threads = []
            for i in range(n_workers):
                thread = threading.Thread(
                    target=upload_worker,
                    args=(file_queue, results_queue, i)
                )
                thread.start()
                threads.append(thread)
            
            # Wait for completion
            for thread in threads:
                thread.join()
            
            total_time = time.time() - start_time
            
            # Collect results
            worker_times = []
            success_count = 0
            while not results_queue.empty():
                worker_id, upload_time, success = results_queue.get()
                if success:
                    worker_times.append(upload_time)
                    success_count += 1
            
            # Calculate statistics
            avg_worker_time = statistics.mean(worker_times) if worker_times else 0
            total_size = sum(f.stat().st_size for f in files)
            speed_mbps = (total_size / (1024 * 1024)) / total_time if total_time > 0 else 0
            
            results[n_workers] = {
                "total_time": total_time,
                "avg_worker_time": avg_worker_time,
                "success_count": success_count,
                "total_files": len(files),
                "total_size_mb": total_size / (1024 * 1024),
                "speed_mbps": speed_mbps
            }
            
            print(f"  Total time: {total_time:.3f}s")
            print(f"  Average worker time: {avg_worker_time:.3f}s")
            print(f"  Success rate: {success_count}/{len(files)}")
            print(f"  Speed: {speed_mbps:.2f} MB/s")
        
        return results
    
    def generate_report(self, single_results: Dict, dir_results: Dict, 
                       concurrent_results: Dict):
        """Generate a comprehensive performance report."""
        print("\n" + "="*80)
        print("PERFORMANCE BENCHMARK REPORT")
        print("="*80)
        
        # Single file performance
        print("\n1. SINGLE FILE UPLOAD PERFORMANCE:")
        print("-" * 40)
        for size_name, result in single_results.items():
            print(f"{size_name:>8}: {result['speed_mbps']:>8.2f} MB/s "
                  f"({result['avg_time']:>6.3f}s)")
        
        # Directory upload performance
        print("\n2. DIRECTORY UPLOAD PERFORMANCE:")
        print("-" * 40)
        print("Threads | Time (s) | Speed (MB/s) | Objects")
        print("-" * 40)
        for threads, result in sorted(dir_results.items()):
            print(f"{threads:>7} | {result['upload_time']:>8.3f} | "
                  f"{result['speed_mbps']:>11.2f} | {result['object_count']:>7}")
        
        # Concurrent upload performance
        print("\n3. CONCURRENT UPLOAD PERFORMANCE:")
        print("-" * 40)
        print("Workers | Total Time (s) | Speed (MB/s) | Success Rate")
        print("-" * 40)
        for workers, result in sorted(concurrent_results.items()):
            success_rate = f"{result['success_count']}/{result['total_files']}"
            print(f"{workers:>7} | {result['total_time']:>14.3f} | "
                  f"{result['speed_mbps']:>11.2f} | {success_rate:>12}")
        
        # Performance recommendations
        print("\n4. PERFORMANCE RECOMMENDATIONS:")
        print("-" * 40)
        
        # Best thread count for directory uploads
        if dir_results:
            best_threads = max(dir_results.keys(), 
                             key=lambda x: dir_results[x]['speed_mbps'])
            print(f"• Optimal thread count for directory uploads: {best_threads}")
        
        # Best worker count for concurrent uploads
        if concurrent_results:
            best_workers = max(concurrent_results.keys(),
                             key=lambda x: concurrent_results[x]['speed_mbps'])
            print(f"• Optimal worker count for concurrent uploads: {best_workers}")
        
        # Speed comparison
        if single_results and dir_results:
            single_speed = single_results['large']['speed_mbps']
            dir_speed = max(r['speed_mbps'] for r in dir_results.values())
            speedup = dir_speed / single_speed if single_speed > 0 else 0
            print(f"• Directory uploads are {speedup:.1f}x faster than single file uploads")


def main():
    """Run the performance benchmark."""
    try:
        benchmark = PerformanceBenchmark()
        
        # Run benchmarks
        single_results = benchmark.benchmark_single_files()
        dir_results = benchmark.benchmark_directory_uploads()
        concurrent_results = benchmark.benchmark_concurrent_uploads()
        
        # Generate report
        benchmark.generate_report(single_results, dir_results, concurrent_results)
        
    except Exception as e:
        print(f"Benchmark failed: {e}")
        raise


if __name__ == "__main__":
    main()
