#!/usr/bin/env python3
"""
Example script demonstrating Google Cloud Storage functionality using cloudbulkupload.
This script shows how to use the BulkGoogleStorage class for bulk operations.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the Google Storage module
from cloudbulkupload import BulkGoogleStorage, StorageTransferPath

async def google_storage_example():
    """Demonstrate Google Cloud Storage functionality."""
    print("🚀 Google Cloud Storage Example")
    print("=" * 50)
    
    # Get Google Cloud configuration from environment
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    credentials_path = os.getenv("GOOGLE_CLOUD_CREDENTIALS_PATH")
    credentials_json = os.getenv("GOOGLE_CLOUD_CREDENTIALS_JSON")
    
    if not project_id:
        print("❌ Error: GOOGLE_CLOUD_PROJECT_ID not found in environment")
        print("Please set your Google Cloud project ID in the .env file")
        return False
    
    # Check if we have either credentials method
    if not credentials_path and not credentials_json:
        print("❌ Error: No Google Cloud credentials found in environment")
        print("Please set either GOOGLE_CLOUD_CREDENTIALS_PATH or GOOGLE_CLOUD_CREDENTIALS_JSON in the .env file")
        print("Or use Application Default Credentials (gcloud auth application-default login)")
        return False
    
    # Initialize Google Storage client using environment variables
    google_client = BulkGoogleStorage(
        project_id=project_id,
        credentials_path=credentials_path,
        credentials_json=credentials_json,
        max_concurrent_operations=50,
        verbose=True
    )
    
    # Bucket name for testing
    bucket_name = "cloudbulkupload-example"
    
    try:
        # Create bucket
        print(f"\n📦 Creating bucket: {bucket_name}")
        await google_client.create_bucket(bucket_name)
        
        # Create test files
        print("\n📁 Creating test files...")
        test_files = []
        for i in range(5):
            filename = f"test_file_{i}.txt"
            content = f"This is test file {i} with some content for Google Cloud Storage testing."
            with open(filename, "w") as f:
                f.write(content)
            test_files.append(filename)
        
        # Upload individual files
        print("\n⬆️  Uploading individual files...")
        upload_paths = [
            StorageTransferPath(
                local_path=filename,
                storage_path=f"individual/{filename}"
            )
            for filename in test_files
        ]
        
        await google_client.upload_files(bucket_name, upload_paths)
        print("✅ Individual files uploaded successfully")
        
        # Upload directory
        print("\n📂 Creating test directory...")
        test_dir = "test_directory"
        os.makedirs(test_dir, exist_ok=True)
        
        for i in range(3):
            subdir = os.path.join(test_dir, f"subdir_{i}")
            os.makedirs(subdir, exist_ok=True)
            
            for j in range(2):
                filename = os.path.join(subdir, f"file_{j}.txt")
                with open(filename, "w") as f:
                    f.write(f"File {j} in subdirectory {i}")
        
        print("⬆️  Uploading directory...")
        await google_client.upload_directory(
            bucket_name=bucket_name,
            local_dir=test_dir,
            storage_dir="directory_upload"
        )
        print("✅ Directory uploaded successfully")
        
        # List blobs
        print("\n📋 Listing blobs in bucket...")
        blobs = await google_client.list_blobs(bucket_name)
        print(f"Found {len(blobs)} blobs:")
        for blob in blobs[:10]:  # Show first 10
            print(f"  - {blob}")
        if len(blobs) > 10:
            print(f"  ... and {len(blobs) - 10} more")
        
        # Download files
        print("\n⬇️  Downloading files...")
        download_dir = "google_download"
        os.makedirs(download_dir, exist_ok=True)
        
        download_paths = [
            StorageTransferPath(
                local_path=os.path.join(download_dir, filename),
                storage_path=f"individual/{filename}"
            )
            for filename in test_files
        ]
        
        await google_client.download_files(bucket_name, download_paths)
        print("✅ Files downloaded successfully")
        
        # Download directory
        print("\n📂 Downloading directory...")
        await google_client.download_directory(
            bucket_name=bucket_name,
            storage_dir="directory_upload",
            local_dir=os.path.join(download_dir, "downloaded_directory")
        )
        print("✅ Directory downloaded successfully")
        
        # Check if blob exists
        print("\n🔍 Checking blob existence...")
        exists = await google_client.check_blob_exists(
            bucket_name=bucket_name,
            blob_name="individual/test_file_0.txt"
        )
        print(f"Blob 'individual/test_file_0.txt' exists: {exists}")
        
        # Clean up
        print("\n🧹 Cleaning up...")
        
        # Remove downloaded files
        import shutil
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)
        
        # Remove test files
        for filename in test_files:
            if os.path.exists(filename):
                os.remove(filename)
        
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        # Empty bucket
        await google_client.empty_bucket(bucket_name)
        print("✅ Bucket emptied")
        
        print("\n🎉 Google Cloud Storage example completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def bulk_upload_example():
    """Demonstrate the bulk_upload_blobs convenience function."""
    print("\n🚀 Bulk Upload Example")
    print("=" * 30)
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    credentials_path = os.getenv("GOOGLE_CLOUD_CREDENTIALS_PATH")
    credentials_json = os.getenv("GOOGLE_CLOUD_CREDENTIALS_JSON")
    
    if not project_id:
        print("❌ Google Cloud project ID not configured")
        return False
    
    # Check if we have credentials
    if not credentials_path and not credentials_json:
        print("❌ Google Cloud credentials not configured")
        return False
    
    # Create test files
    test_files = []
    for i in range(3):
        filename = f"bulk_test_{i}.txt"
        with open(filename, "w") as f:
            f.write(f"Bulk upload test file {i}")
        test_files.append(filename)
    
    try:
        # Use the convenience function with environment variables
        from cloudbulkupload import google_bulk_upload_blobs
        
        await google_bulk_upload_blobs(
            project_id=project_id,
            bucket_name="bulk-upload-test",
            files_to_upload=test_files,
            credentials_path=credentials_path,
            credentials_json=credentials_json,
            max_concurrent=10,
            verbose=True
        )
        
        print("✅ Bulk upload completed successfully")
        
        # Clean up
        for filename in test_files:
            if os.path.exists(filename):
                os.remove(filename)
        
        return True
        
    except Exception as e:
        print(f"❌ Bulk upload error: {e}")
        return False


async def main():
    """Main function to run Google Cloud Storage examples."""
    print("Google Cloud Storage Examples for cloudbulkupload")
    print("=" * 60)
    
    # Check if Google Cloud is configured
    if not os.getenv("GOOGLE_CLOUD_PROJECT_ID"):
        print("❌ Google Cloud project ID not configured")
        print("\nTo run Google Cloud examples, please:")
        print("1. Add GOOGLE_CLOUD_PROJECT_ID to your .env file")
        print("2. Optionally add GOOGLE_CLOUD_CREDENTIALS_PATH for service account file authentication")
        print("3. Optionally add GOOGLE_CLOUD_CREDENTIALS_JSON for service account JSON string authentication")
        print("4. Or use Application Default Credentials (gcloud auth application-default login)")
        return
    
    # Run examples
    success1 = await google_storage_example()
    success2 = await bulk_upload_example()
    
    if success1 and success2:
        print("\n🎉 All Google Cloud Storage examples completed successfully!")
    else:
        print("\n⚠️  Some examples failed. Check the output above for details.")


if __name__ == "__main__":
    asyncio.run(main())
