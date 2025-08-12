# Azure Blob Storage Guide for cloudbulkupload

This guide covers the Azure Blob Storage functionality in the `cloudbulkupload` package, including async operations, performance optimization, and comparison with AWS S3.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Basic Usage](#basic-usage)
5. [Advanced Usage](#advanced-usage)
6. [Performance Optimization](#performance-optimization)
7. [Comparison with AWS S3](#comparison-with-aws-s3)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)

## Overview

The `cloudbulkupload` package now supports Azure Blob Storage with async operations, providing:

- **Async/Await Support**: Full async/await pattern for better performance
- **Bulk Operations**: Upload and download multiple files concurrently
- **Directory Operations**: Upload and download entire directories
- **Progress Tracking**: Built-in progress bars for long operations
- **Error Handling**: Comprehensive error handling and retry logic
- **Performance Optimization**: Configurable concurrency limits

### Key Features

- **BulkAzureBlob Class**: Main class for Azure Blob Storage operations
- **Async Operations**: All operations are async for better performance
- **Concurrency Control**: Semaphore-based concurrency limiting
- **Progress Bars**: Optional progress tracking with tqdm
- **Error Recovery**: Graceful error handling and logging

## Installation

### Prerequisites

- Python 3.11 or higher
- Azure Storage account
- Azure Storage connection string

### Install Package

```bash
# Install with Azure support
pip install cloudbulkupload

# Install with test dependencies
pip install "cloudbulkupload[test]"
```

### Azure SDK Dependencies

The package automatically installs:
- `azure-storage-blob>=12.0.0`
- `azure-core` (for exception handling)

## Configuration

### Environment Variables

Create a `.env` file with your Azure credentials:

```env
# Azure Storage Configuration
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net

# Optional: AWS S3 for comparison testing
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_ENDPOINT_URL=http://localhost:9000
```

### Connection String Format

Your Azure Storage connection string should follow this format:
```
DefaultEndpointsProtocol=https;AccountName=YOUR_ACCOUNT_NAME;AccountKey=YOUR_ACCOUNT_KEY;EndpointSuffix=core.windows.net
```

## Basic Usage

### Initialize Azure Client

```python
import asyncio
from cloudbulkupload import BulkAzureBlob

async def main():
    # Initialize Azure client
    azure_client = BulkAzureBlob(
        connection_string="your_connection_string",
        max_concurrent_operations=50,
        verbose=True
    )
    
    # Your operations here...

# Run the async function
asyncio.run(main())
```

### Upload Files

```python
from cloudbulkupload import StorageTransferPath

# Upload single file
upload_path = StorageTransferPath(
    local_path="local_file.txt",
    storage_path="container/path/file.txt"
)

await azure_client.upload_files(
    container_name="my-container",
    upload_paths=upload_path
)

# Upload multiple files
upload_paths = [
    StorageTransferPath("file1.txt", "container/file1.txt"),
    StorageTransferPath("file2.txt", "container/file2.txt"),
    StorageTransferPath("file3.txt", "container/file3.txt")
]

await azure_client.upload_files(
    container_name="my-container",
    upload_paths=upload_paths
)
```

### Download Files

```python
# Download single file
download_path = StorageTransferPath(
    local_path="downloaded_file.txt",
    storage_path="container/path/file.txt"
)

await azure_client.download_files(
    container_name="my-container",
    download_paths=download_path
)

# Download multiple files
download_paths = [
    StorageTransferPath("local1.txt", "container/file1.txt"),
    StorageTransferPath("local2.txt", "container/file2.txt")
]

await azure_client.download_files(
    container_name="my-container",
    download_paths=download_paths
)
```

### Directory Operations

```python
# Upload entire directory
await azure_client.upload_directory(
    container_name="my-container",
    local_dir="local_directory",
    storage_dir="container/path"
)

# Download entire directory
await azure_client.download_directory(
    container_name="my-container",
    storage_dir="container/path",
    local_dir="downloaded_directory"
)
```

## Advanced Usage

### Container Management

```python
# Create container
await azure_client.create_container("new-container")

# Delete container (and all blobs)
await azure_client.delete_container("old-container")

# Empty container (delete all blobs)
await azure_client.empty_container("my-container")
```

### Blob Operations

```python
# List blobs in container
blobs = await azure_client.list_blobs("my-container")
for blob in blobs:
    print(f"Blob: {blob}")

# List blobs in specific directory
blobs = await azure_client.list_blobs(
    container_name="my-container",
    storage_dir="my-directory"
)

# Check if blob exists
exists = await azure_client.check_blob_exists(
    container_name="my-container",
    blob_name="path/to/blob.txt"
)
```

### Convenience Functions

```python
from cloudbulkupload import bulk_upload_blobs, bulk_download_blobs

# Bulk upload files
files_to_upload = ["file1.txt", "file2.txt", "file3.txt"]
await bulk_upload_blobs(
    connection_string="your_connection_string",
    container_name="my-container",
    files_to_upload=files_to_upload,
    max_concurrent=50,
    verbose=True
)

# Bulk download blobs
blob_names = ["blob1.txt", "blob2.txt", "blob3.txt"]
await bulk_download_blobs(
    connection_string="your_connection_string",
    container_name="my-container",
    blob_names=blob_names,
    local_dir="downloads",
    max_concurrent=50,
    verbose=True
)
```

## Performance Optimization

### Concurrency Settings

```python
# High concurrency for fast uploads
azure_client = BulkAzureBlob(
    connection_string="your_connection_string",
    max_concurrent_operations=100,  # More concurrent operations
    verbose=True
)

# Lower concurrency for stability
azure_client = BulkAzureBlob(
    connection_string="your_connection_string",
    max_concurrent_operations=10,   # Fewer concurrent operations
    verbose=True
)
```

### Best Practices

1. **Concurrency Tuning**: Start with 50 concurrent operations and adjust based on your network and Azure limits
2. **File Size**: Larger files benefit more from concurrent uploads
3. **Network**: Ensure stable, high-bandwidth connection
4. **Azure Limits**: Be aware of Azure Storage account limits

### Performance Monitoring

```python
import time

# Monitor upload performance
start_time = time.time()
await azure_client.upload_files(container_name, upload_paths)
elapsed_time = time.time() - start_time

total_size = sum(os.path.getsize(f.local_path) for f in upload_paths)
speed = total_size / (1024 * 1024 * elapsed_time)  # MB/s
print(f"Upload speed: {speed:.2f} MB/s")
```

## Comparison with AWS S3

### Feature Comparison

| Feature | AWS S3 (BulkBoto3) | Azure Blob (BulkAzureBlob) |
|---------|-------------------|----------------------------|
| **Concurrency Model** | Thread-based | Async/Await |
| **Progress Tracking** | ✅ | ✅ |
| **Directory Operations** | ✅ | ✅ |
| **Bulk Operations** | ✅ | ✅ |
| **Error Handling** | ✅ | ✅ |
| **Performance** | Thread-limited | Async-optimized |

### Performance Comparison

Run the performance comparison test:

```bash
# Run Azure vs AWS performance comparison
python run_tests.py --type azure-comparison
```

This will:
- Test both platforms with various file sizes and counts
- Measure upload and download speeds
- Generate comparison reports
- Save results to CSV

### When to Use Each

**Use AWS S3 (BulkBoto3) when:**
- You need thread-based concurrency
- Working with existing AWS infrastructure
- Need S3-specific features

**Use Azure Blob (BulkAzureBlob) when:**
- You want async/await performance
- Working with Azure infrastructure
- Need Azure-specific features
- Want better resource utilization

## Examples

### Complete Example

```python
import asyncio
import os
from cloudbulkupload import BulkAzureBlob, StorageTransferPath
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def complete_example():
    # Initialize client
    azure_client = BulkAzureBlob(
        connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
        max_concurrent_operations=50,
        verbose=True
    )
    
    container_name = "example-container"
    
    try:
        # Create container
        await azure_client.create_container(container_name)
        
        # Create test files
        test_files = []
        for i in range(5):
            filename = f"test_file_{i}.txt"
            with open(filename, "w") as f:
                f.write(f"Test content {i}")
            test_files.append(filename)
        
        # Upload files
        upload_paths = [
            StorageTransferPath(filename, f"uploads/{filename}")
            for filename in test_files
        ]
        
        await azure_client.upload_files(container_name, upload_paths)
        print("✅ Files uploaded successfully")
        
        # List blobs
        blobs = await azure_client.list_blobs(container_name)
        print(f"📋 Found {len(blobs)} blobs")
        
        # Download files
        download_paths = [
            StorageTransferPath(f"downloaded_{filename}", f"uploads/{filename}")
            for filename in test_files
        ]
        
        await azure_client.download_files(container_name, download_paths)
        print("✅ Files downloaded successfully")
        
        # Clean up
        for filename in test_files:
            if os.path.exists(filename):
                os.remove(filename)
            if os.path.exists(f"downloaded_{filename}"):
                os.remove(f"downloaded_{filename}")
        
        await azure_client.empty_container(container_name)
        print("✅ Cleanup completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")

# Run the example
if __name__ == "__main__":
    asyncio.run(complete_example())
```

### Error Handling Example

```python
async def robust_upload_example():
    azure_client = BulkAzureBlob(
        connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
        max_concurrent_operations=10,  # Lower concurrency for stability
        verbose=True
    )
    
    try:
        # Upload with error handling
        await azure_client.upload_files(
            container_name="my-container",
            upload_paths=upload_paths
        )
    except Exception as e:
        print(f"Upload failed: {e}")
        # Implement retry logic or fallback
        return False
    
    return True
```

## Troubleshooting

### Common Issues

#### 1. Connection String Issues
**Error**: `ValueError: Invalid connection string`
**Solution**: Verify your connection string format and credentials

#### 2. Container Not Found
**Error**: `ResourceNotFoundError: The specified container does not exist`
**Solution**: Create the container first or use `create_container()`

#### 3. Permission Issues
**Error**: `HttpResponseError: Server failed to authenticate the request`
**Solution**: Check your Azure Storage account key and permissions

#### 4. Concurrency Issues
**Error**: `Too many requests` or timeouts
**Solution**: Reduce `max_concurrent_operations`

#### 5. File Not Found
**Error**: `FileNotFoundError: File not found`
**Solution**: Verify local file paths exist

### Debug Mode

Enable verbose logging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

azure_client = BulkAzureBlob(
    connection_string="your_connection_string",
    verbose=True  # Enable progress bars and detailed logging
)
```

### Performance Issues

1. **Slow Uploads**: Increase `max_concurrent_operations`
2. **Memory Issues**: Reduce `max_concurrent_operations`
3. **Network Timeouts**: Check network stability and Azure region
4. **Rate Limiting**: Implement exponential backoff

### Getting Help

1. **Check Logs**: Enable verbose mode for detailed logs
2. **Test Connection**: Use Azure Storage Explorer to verify connectivity
3. **Monitor Performance**: Use the performance comparison test
4. **Azure Documentation**: Refer to [Azure Storage documentation](https://docs.microsoft.com/en-us/azure/storage/)

## Integration with Existing Code

### Migration from AWS S3

```python
# Old AWS S3 code
bulkboto = BulkBoto3(endpoint_url, access_key, secret_key)
bulkboto.upload(bucket_name, upload_paths)

# New Azure Blob code
azure_client = BulkAzureBlob(connection_string)
await azure_client.upload_files(container_name, upload_paths)
```

### Hybrid Approach

```python
# Use both AWS S3 and Azure Blob
aws_client = BulkBoto3(endpoint_url, access_key, secret_key)
azure_client = BulkAzureBlob(connection_string)

# Choose based on requirements
if use_azure:
    await azure_client.upload_files(container_name, upload_paths)
else:
    aws_client.upload(bucket_name, upload_paths)
```

---

**For more information, see:**
- [Azure Storage Blob documentation](https://docs.microsoft.com/en-us/azure/storage/blobs/)
- [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python)
- [Performance comparison results](performance_comparison_results.csv)
