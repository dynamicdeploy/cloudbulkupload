# Google Cloud Storage Guide for cloudbulkupload

## 🚀 Overview

The `cloudbulkupload` package provides comprehensive Google Cloud Storage support with two upload modes:

1. **Standard Async Mode** - Our custom async implementation (consistent API across providers)
2. **High-Performance Mode** - Google's Transfer Manager (up to 50% faster, Google-specific)

## 🔧 Installation

```bash
pip install cloudbulkupload[google-cloud]
```

## 🔐 Authentication

### Method 1: Service Account JSON File (Recommended for Development)
```python
import os
from dotenv import load_dotenv
from cloudbulkupload import BulkGoogleStorage

load_dotenv()

google_client = BulkGoogleStorage(
    project_id=os.getenv("GOOGLE_CLOUD_PROJECT_ID"),
    credentials_path=os.getenv("GOOGLE_CLOUD_CREDENTIALS_PATH"),
    max_concurrent_operations=50,
    verbose=True
)
```

### Method 2: Service Account JSON String (Recommended for Cloud/Container Environments)
```python
# Set environment variable with JSON string
export GOOGLE_CLOUD_CREDENTIALS_JSON='{"type":"service_account","project_id":"...","private_key_id":"...","private_key":"...","client_email":"...","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}'

# Or use in code
google_client = BulkGoogleStorage(
    project_id="your-project-id",
    credentials_json='{"type":"service_account",...}'
)
```

### Method 3: Application Default Credentials
```python
# Use gcloud auth application-default login
google_client = BulkGoogleStorage(
    project_id="your-project-id"
)
```

## 📁 Basic Usage

### Standard Mode (Consistent API)
```python
import asyncio
from cloudbulkupload import BulkGoogleStorage, StorageTransferPath

async def main():
    # Initialize client
    client = BulkGoogleStorage(
        project_id="your-project-id",
        credentials_path="./service-account.json",
        max_concurrent_operations=50,
        verbose=True
    )
    
    # Create upload paths
    upload_paths = [
        StorageTransferPath(
            local_path="./file1.txt",
            storage_path="uploads/file1.txt"
        ),
        StorageTransferPath(
            local_path="./file2.txt", 
            storage_path="uploads/file2.txt"
        )
    ]
    
    # Upload files (standard mode)
    await client.upload_files("your-bucket", upload_paths)
    
    # Download files
    download_paths = [
        StorageTransferPath(
            local_path="./downloaded/file1.txt",
            storage_path="uploads/file1.txt"
        )
    ]
    await client.download_files("your-bucket", download_paths)
    
    # List files
    blobs = await client.list_blobs("your-bucket")
    print(f"Found {len(blobs)} files")
    
    # Check if file exists
    exists = await client.check_blob_exists("your-bucket", "uploads/file1.txt")
    print(f"File exists: {exists}")

asyncio.run(main())
```

### High-Performance Mode (Transfer Manager)
```python
async def main():
    client = BulkGoogleStorage(
        project_id="your-project-id",
        credentials_path="./service-account.json",
        verbose=True
    )
    
    upload_paths = [
        StorageTransferPath(
            local_path="./large_file1.txt",
            storage_path="uploads/large_file1.txt"
        ),
        StorageTransferPath(
            local_path="./large_file2.txt",
            storage_path="uploads/large_file2.txt"
        )
    ]
    
    # Upload files with Transfer Manager (up to 50% faster!)
    await client.upload_files(
        "your-bucket", 
        upload_paths, 
        use_transfer_manager=True  # 🚀 High-performance mode
    )

asyncio.run(main())
```

## 🚀 Convenience Functions

### Standard Mode
```python
from cloudbulkupload import google_bulk_upload_blobs, google_bulk_download_blobs

# Upload files
await google_bulk_upload_blobs(
    project_id="your-project-id",
    bucket_name="your-bucket",
    files_to_upload=["./file1.txt", "./file2.txt"],
    credentials_path="./service-account.json",
    max_concurrent=50,
    verbose=True
)

# Download files
await google_bulk_download_blobs(
    project_id="your-project-id",
    bucket_name="your-bucket",
    blob_names=["uploads/file1.txt", "uploads/file2.txt"],
    local_dir="./downloads",
    credentials_path="./service-account.json",
    max_concurrent=50,
    verbose=True
)
```

### High-Performance Mode
```python
# Upload with Transfer Manager
await google_bulk_upload_blobs(
    project_id="your-project-id",
    bucket_name="your-bucket",
    files_to_upload=["./large_file1.txt", "./large_file2.txt"],
    credentials_path="./service-account.json",
    max_concurrent=50,
    verbose=True,
    use_transfer_manager=True  # 🚀 High-performance mode
)
```

## 📊 Performance Comparison

| Mode | Speed | API Consistency | Features | Use Case |
|------|-------|-----------------|----------|----------|
| **Standard** | Good (5.94 MB/s) | ✅ Perfect | ✅ Complete | Multi-cloud, consistent API |
| **Transfer Manager** | Excellent (8.87 MB/s) | ❌ Google-only | ❌ Upload only | Google Cloud, max performance |

### When to Use Each Mode

#### Use Standard Mode When:
- ✅ **Multi-cloud applications** (AWS + Azure + Google)
- ✅ **Need consistent API** across providers
- ✅ **Require full feature set** (upload, download, list, delete)
- ✅ **Want unified error handling**
- ✅ **Learning curve matters**

#### Use Transfer Manager Mode When:
- 🚀 **Google Cloud only** applications
- 🚀 **Maximum performance** is critical
- 🚀 **Large file uploads** (100MB+ files)
- 🚀 **Bulk operations** (100+ files)
- 🚀 **Performance optimization** is priority

## 🔄 Migration Guide

### From Standard to Transfer Manager
```python
# Before (Standard Mode)
await client.upload_files(bucket_name, upload_paths)

# After (Transfer Manager Mode)
await client.upload_files(bucket_name, upload_paths, use_transfer_manager=True)
```

### From Transfer Manager to Standard
```python
# Before (Transfer Manager Mode)
await client.upload_files(bucket_name, upload_paths, use_transfer_manager=True)

# After (Standard Mode)
await client.upload_files(bucket_name, upload_paths)  # Default is False
```

## 🧪 Testing

### Run Google Cloud Tests
```bash
# Basic functionality
python run_tests.py --type google-cloud

# Performance comparison
python run_tests.py --type three-way-comparison
```

### Test Both Modes
```python
import asyncio
from cloudbulkupload import BulkGoogleStorage, StorageTransferPath

async def test_both_modes():
    client = BulkGoogleStorage(
        project_id="your-project-id",
        credentials_path="./service-account.json",
        verbose=True
    )
    
    upload_paths = [
        StorageTransferPath(
            local_path="./test_file.txt",
            storage_path="test/test_file.txt"
        )
    ]
    
    # Test standard mode
    print("Testing Standard Mode...")
    await client.upload_files("test-bucket", upload_paths)
    
    # Test transfer manager mode
    print("Testing Transfer Manager Mode...")
    await client.upload_files("test-bucket", upload_paths, use_transfer_manager=True)

asyncio.run(test_both_modes())
```

## 🎯 Best Practices

### 1. Choose the Right Mode
```python
# For multi-cloud applications
if provider == "google" and performance_critical:
    use_transfer_manager = True
else:
    use_transfer_manager = False

await client.upload_files(bucket, files, use_transfer_manager=use_transfer_manager)
```

### 2. Environment Configuration
```env
# .env file
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_CREDENTIALS_PATH=./service-account.json
# OR
GOOGLE_CLOUD_CREDENTIALS_JSON={"type":"service_account",...}
```

### 3. Error Handling
```python
try:
    await client.upload_files(bucket, files, use_transfer_manager=True)
except Exception as e:
    # Transfer Manager failed, fall back to standard mode
    print(f"Transfer Manager failed: {e}")
    await client.upload_files(bucket, files, use_transfer_manager=False)
```

## 🚀 Performance Tips

1. **Use Transfer Manager** for large files (>100MB) or bulk uploads (>100 files)
2. **Standard mode** is sufficient for small files and multi-cloud scenarios
3. **Monitor performance** and switch modes based on your specific use case
4. **Test both modes** to find the optimal configuration for your workload

## 📚 Additional Resources

- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [Transfer Manager Documentation](https://cloud.google.com/storage/docs/transfer-manager)
- [Service Account Setup](https://cloud.google.com/iam/docs/service-accounts)
- [Performance Best Practices](https://cloud.google.com/storage/docs/best-practices)

---

**🎉 You now have the best of both worlds: consistent API with optional high-performance mode!**
