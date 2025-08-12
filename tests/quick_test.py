#!/usr/bin/env python3
"""
Quick test script for fast validation of cloudbulkupload functionality.
This script runs a minimal set of tests to verify the package works correctly.
"""

import os
import time
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from cloudbulkupload import BulkBoto3, StorageTransferPath
try:
    from test_config import get_test_config
except ImportError:
    from tests.test_config import get_test_config

# Load environment variables
load_dotenv()


def quick_test():
    """Run a quick test to validate the package functionality."""
    print("🚀 Running Quick Test for cloudbulkupload")
    print("=" * 50)
    
    # Load test configuration
    config = get_test_config()
    config.print_config()
    
    # Check environment
    endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:9000")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    if not access_key or not secret_key:
        print("❌ Error: AWS credentials not found in .env file")
        return False
    
    print(f"✅ Using endpoint: {endpoint_url}")
    
    # Initialize BulkBoto3
    try:
        bulkboto = BulkBoto3(
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            max_pool_connections=config.max_threads,
            verbose=config.verbose_tests
        )
        print("✅ BulkBoto3 initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize BulkBoto3: {e}")
        return False
    
    # Test bucket operations
    test_bucket = "quick-test-bucket"
    try:
        bulkboto.create_new_bucket(test_bucket)
        print("✅ Bucket created successfully")
    except Exception as e:
        print(f"❌ Failed to create bucket: {e}")
        return False
    
    # Create test file
    test_dir = tempfile.mkdtemp(prefix="quick_test_")
    test_file = Path(test_dir) / "test.txt"
    test_file.write_text("Hello, cloudbulkupload!")
    
    # Test single file upload
    try:
        start_time = time.time()
        bulkboto.upload(
            bucket_name=test_bucket,
            upload_paths=StorageTransferPath(
                local_path=str(test_file),
                storage_path="test.txt"
            )
        )
        upload_time = time.time() - start_time
        
        # Verify upload
        exists = bulkboto.check_object_exists(
            bucket_name=test_bucket,
            object_path="test.txt"
        )
        
        if exists:
            print(f"✅ Single file upload successful ({upload_time:.3f}s)")
        else:
            print("❌ File upload verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Single file upload failed: {e}")
        return False
    
    # Test directory upload
    try:
        # Create a few more files
        for i in range(3):
            (Path(test_dir) / f"file_{i}.txt").write_text(f"Content {i}")
        
        start_time = time.time()
        bulkboto.upload_dir_to_storage(
            bucket_name=test_bucket,
            local_dir=test_dir,
            storage_dir="quick_test_dir",
            n_threads=5
        )
        dir_upload_time = time.time() - start_time
        
        # Verify directory upload
        objects = bulkboto.list_objects(
            bucket_name=test_bucket,
            storage_dir="quick_test_dir"
        )
        
        if len(objects) >= 4:  # test.txt + 3 additional files
            print(f"✅ Directory upload successful ({dir_upload_time:.3f}s, {len(objects)} objects)")
        else:
            print(f"❌ Directory upload verification failed (expected >=4, got {len(objects)})")
            return False
            
    except Exception as e:
        print(f"❌ Directory upload failed: {e}")
        return False
    
    # Test download
    try:
        download_dir = tempfile.mkdtemp(prefix="quick_download_")
        start_time = time.time()
        bulkboto.download_dir_from_storage(
            bucket_name=test_bucket,
            storage_dir="quick_test_dir",
            local_dir=download_dir,
            n_threads=5
        )
        download_time = time.time() - start_time
        
        downloaded_files = list(Path(download_dir).glob("*"))
        if len(downloaded_files) >= 1:  # At least one file should be downloaded
            print(f"✅ Directory download successful ({download_time:.3f}s, {len(downloaded_files)} files)")
        else:
            print(f"❌ Directory download verification failed (expected >=1, got {len(downloaded_files)})")
            return False
            
    except Exception as e:
        print(f"❌ Directory download failed: {e}")
        return False
    
    # Cleanup based on configuration
    if config.should_cleanup("buckets"):
        try:
            print(config.get_cleanup_message("buckets"))
            bulkboto.empty_bucket(test_bucket)
            bulkboto.resource.Bucket(test_bucket).delete()
            print("✅ Bucket cleanup completed")
        except Exception as e:
            print(f"⚠️  Bucket cleanup warning: {e}")
    else:
        print(config.get_cleanup_message("buckets"))
    
    if config.should_cleanup("local_files"):
        try:
            print(config.get_cleanup_message("local_files"))
            import shutil
            shutil.rmtree(test_dir, ignore_errors=True)
            shutil.rmtree(download_dir, ignore_errors=True)
            print("✅ Local files cleanup completed")
        except Exception as e:
            print(f"⚠️  Local files cleanup warning: {e}")
    else:
        print(config.get_cleanup_message("local_files"))
    
    print("\n🎉 Quick test completed successfully!")
    print("=" * 50)
    return True


if __name__ == "__main__":
    success = quick_test()
    exit(0 if success else 1)
