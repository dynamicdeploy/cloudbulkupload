#!/usr/bin/env python3
"""
Demonstration script showing the expected import and usage pattern for cloudbulkupload.
This script demonstrates how users should import and use the package after installation.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Expected import pattern
from cloudbulkupload import BulkBoto3, StorageTransferPath

def demo_import_and_usage():
    """Demonstrate the expected import and usage pattern."""
    print("🚀 cloudbulkupload Import and Usage Demo")
    print("=" * 50)
    
    # Check environment
    endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:9000")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    if not access_key or not secret_key:
        print("❌ Error: AWS credentials not found in .env file")
        return False
    
    print(f"✅ Using endpoint: {endpoint_url}")
    
    # Initialize BulkBoto3 (expected usage)
    try:
        bulkboto = BulkBoto3(
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            max_pool_connections=50,
            verbose=False
        )
        print("✅ BulkBoto3 initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize BulkBoto3: {e}")
        return False
    
    # Test bucket operations
    test_bucket = "import-demo-bucket"
    try:
        bulkboto.create_new_bucket(test_bucket)
        print("✅ Bucket created successfully")
    except Exception as e:
        print(f"⚠️  Bucket might already exist: {e}")
    
    # Test StorageTransferPath usage
    try:
        # Create a test file
        test_file = "test_import_demo.txt"
        with open(test_file, "w") as f:
            f.write("This is a test file for import demo")
        
        # Use StorageTransferPath (expected usage)
        upload_path = StorageTransferPath(
            local_path=test_file,
            storage_path="demo/test_file.txt"
        )
        
        # Upload using the path
        bulkboto.upload(
            bucket_name=test_bucket,
            upload_paths=upload_path
        )
        print("✅ File uploaded successfully using StorageTransferPath")
        
        # Clean up test file
        os.remove(test_file)
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False
    
    # Clean up bucket
    try:
        bulkboto.empty_bucket(test_bucket)
        bulkboto.resource.Bucket(test_bucket).delete()
        print("✅ Bucket cleanup completed")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")
    
    print("\n🎉 Import and usage demo completed successfully!")
    print("\n📝 Expected Usage Pattern:")
    print("   pip install cloudbulkupload")
    print("   from cloudbulkupload import BulkBoto3, StorageTransferPath")
    print("   bulkboto = BulkBoto3(...)")
    print("   path = StorageTransferPath(...)")
    print("   bulkboto.upload(bucket_name='bucket', upload_paths=path)")
    
    return True

if __name__ == "__main__":
    success = demo_import_and_usage()
    exit(0 if success else 1)
