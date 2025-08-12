#!/usr/bin/env python3
"""
Example script demonstrating Azure Blob Storage functionality using cloudbulkupload.
This script shows how to use the BulkAzureBlob class for bulk operations.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the Azure module
from cloudbulkupload import BulkAzureBlob, StorageTransferPath

async def azure_blob_example():
    """Demonstrate Azure Blob Storage functionality."""
    print("🚀 Azure Blob Storage Example")
    print("=" * 50)
    
    # Get Azure connection string from environment
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        print("❌ Error: AZURE_STORAGE_CONNECTION_STRING not found in environment")
        print("Please set your Azure Storage connection string in the .env file")
        return False
    
    # Initialize Azure client
    azure_client = BulkAzureBlob(
        connection_string=connection_string,
        max_concurrent_operations=50,
        verbose=True
    )
    
    # Container name for testing
    container_name = "cloudbulkupload-example"
    
    try:
        # Create container
        print(f"\n📦 Creating container: {container_name}")
        await azure_client.create_container(container_name)
        
        # Create test files
        print("\n📁 Creating test files...")
        test_files = []
        for i in range(5):
            filename = f"test_file_{i}.txt"
            content = f"This is test file {i} with some content for Azure Blob Storage testing."
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
        
        await azure_client.upload_files(container_name, upload_paths)
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
        await azure_client.upload_directory(
            container_name=container_name,
            local_dir=test_dir,
            storage_dir="directory_upload"
        )
        print("✅ Directory uploaded successfully")
        
        # List blobs
        print("\n📋 Listing blobs in container...")
        blobs = await azure_client.list_blobs(container_name)
        print(f"Found {len(blobs)} blobs:")
        for blob in blobs[:10]:  # Show first 10
            print(f"  - {blob}")
        if len(blobs) > 10:
            print(f"  ... and {len(blobs) - 10} more")
        
        # Download files
        print("\n⬇️  Downloading files...")
        download_dir = "azure_download"
        os.makedirs(download_dir, exist_ok=True)
        
        download_paths = [
            StorageTransferPath(
                local_path=os.path.join(download_dir, filename),
                storage_path=f"individual/{filename}"
            )
            for filename in test_files
        ]
        
        await azure_client.download_files(container_name, download_paths)
        print("✅ Files downloaded successfully")
        
        # Download directory
        print("\n📂 Downloading directory...")
        await azure_client.download_directory(
            container_name=container_name,
            storage_dir="directory_upload",
            local_dir=os.path.join(download_dir, "downloaded_directory")
        )
        print("✅ Directory downloaded successfully")
        
        # Check if blob exists
        print("\n🔍 Checking blob existence...")
        exists = await azure_client.check_blob_exists(
            container_name=container_name,
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
        
        # Empty container
        await azure_client.empty_container(container_name)
        print("✅ Container emptied")
        
        print("\n🎉 Azure Blob Storage example completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def bulk_upload_example():
    """Demonstrate the bulk_upload_blobs convenience function."""
    print("\n🚀 Bulk Upload Example")
    print("=" * 30)
    
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        print("❌ Azure connection string not configured")
        return False
    
    # Create test files
    test_files = []
    for i in range(3):
        filename = f"bulk_test_{i}.txt"
        with open(filename, "w") as f:
            f.write(f"Bulk upload test file {i}")
        test_files.append(filename)
    
    try:
        # Use the convenience function
        from cloudbulkupload import bulk_upload_blobs
        
        await bulk_upload_blobs(
            connection_string=connection_string,
            container_name="bulk-upload-test",
            files_to_upload=test_files,
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
    """Main function to run Azure examples."""
    print("Azure Blob Storage Examples for cloudbulkupload")
    print("=" * 60)
    
    # Check if Azure is configured
    if not os.getenv("AZURE_STORAGE_CONNECTION_STRING"):
        print("❌ Azure Storage connection string not configured")
        print("\nTo run Azure examples, please:")
        print("1. Add AZURE_STORAGE_CONNECTION_STRING to your .env file")
        print("2. Format: DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net")
        return
    
    # Run examples
    success1 = await azure_blob_example()
    success2 = await bulk_upload_example()
    
    if success1 and success2:
        print("\n🎉 All Azure examples completed successfully!")
    else:
        print("\n⚠️  Some examples failed. Check the output above for details.")


if __name__ == "__main__":
    asyncio.run(main())
