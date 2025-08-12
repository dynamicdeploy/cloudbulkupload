<!--# Bulk Boto: Python package for fast and parallel transferring a bulk of files to S3 based on boto3-->
<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/iamirmasoud/bulkboto3">
    <img src="https://raw.githubusercontent.com/iamirmasoud/bulkboto3/main/imgs/logo.png" alt="Logo" width="100" height="100">
  </a>
    
  <h3 align="center">Cloud Bulk Upload (cloudbulkupload)</h3>

  <p align="center">
    Python package for fast and parallel transferring a bulk of files to S3 and Azure Blob Storage!
    <br />
    <!-- 
    <a href="https://github.com/iamirmasoud/bulkboto3"><strong>Explore the docs »</strong></a>
    <br /> 
    -->
    <a href="https://pypi.org/project/cloudbulkupload/">See on PyPI</a>
    ·
    <a href="https://github.com/dynamicdeploy/cloudbulkupload/blob/main/examples.py">View Examples</a>
    ·
    <a href="https://github.com/dynamicdeploy/cloudbulkupload/issues">Report Bug/Request Feature</a>
    

![Python](https://img.shields.io/pypi/pyversions/cloudbulkupload.svg?style=flat&https://pypi.python.org/pypi/cloudbulkupload/)
![Version](http://img.shields.io/pypi/v/cloudbulkupload.svg?style=flat&https://pypi.python.org/pypi/cloudbulkupload/)
![License](http://img.shields.io/pypi/l/cloudbulkupload.svg?style=flat&https://github.com/dynamicdeploy/cloudbulkupload/blob/main/LICENSE)
[![Downloads](https://pepy.tech/badge/cloudbulkupload)](https://pepy.tech/project/cloudbulkupload)   

</p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-cloudbulkupload">About cloudbulkupload</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#azure-blob-storage">Azure Blob Storage</a></li>
    <li><a href="#performance-comparison">Performance Comparison</a></li>
    <li><a href="#blog-posts">Blog Posts</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contributors">Contributors</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

## About cloudbulkupload
[Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) is the official Python SDK
for accessing and managing all AWS resources such as Amazon Simple Storage Service (S3).
Generally, it's pretty ok to transfer a small number of files using Boto3. However, transferring a large number of
small files impede performance. Although it only takes a few milliseconds per file to transfer,
it can take up to hours to transfer hundreds of thousands, or millions, of files if you do it sequentially.
Moreover, because Amazon S3 does not have folders/directories, managing the hierarchy of directories and files
manually can be a bit tedious especially if there are many files located in different folders.

The `cloudbulkupload` package solves these issues. It speeds up transferring of many small files to Amazon AWS S3, Azure Blob Storage, and Google Cloud Storage by
executing multiple download/upload operations in parallel by leveraging the Python multiprocessing module and async/await patterns.
Depending on the number of cores of your machine, Cloud Bulk Upload can make cloud storage transfers even 100X faster than sequential
mode using traditional Boto3! Furthermore, Cloud Bulk Upload can keep the original folder structure of files and
directories when transferring them. There are also some other features as follows.

### Main Functionalities
  - **AWS S3 Support**: Multi-thread uploading/downloading of a directory (keeping the directory structure) to/from S3 object storage
  - **Azure Blob Storage Support**: Async uploading/downloading with configurable concurrency for Azure Blob Storage
  - **Google Cloud Storage Support**: Async uploading/downloading with configurable concurrency for Google Cloud Storage
  - **Cross-Platform Performance**: Performance comparison between AWS S3, Azure Blob Storage, and Google Cloud Storage
  - **Container Management**: Creating, deleting, and managing storage containers/buckets
  - **Object Operations**: Checking existence, listing objects, and bulk operations
  - **Progress Tracking**: Built-in progress bars for long-running operations
  - **Configurable Test Suite**: Comprehensive testing with cleanup options

## Getting Started
### Prerequisites
* [Python 3.11+](https://www.python.org/)
* [pip](https://pip.pypa.io/en/stable/)
* API credentials to access S3 and/or Azure Blob Storage

**Note**:
You can deploy a free S3 server using [MinIO](https://min.io/) 
on your local machine by following the steps explained in: [Deploy Standalone MinIO using Docker Compose on Linux](http://www.sefidian.com/2022/04/08/deploy-standalone-minio-using-docker-compose/).
  
### Installation
Use the package manager [pip](https://pypi.org/project/cloudbulkupload/) to install `cloudbulkupload`.

```bash
pip install cloudbulkupload
```

## Usage
You can find the following scripts in [examples.py](https://github.com/dynamicdeploy/cloudbulkupload/blob/main/examples.py) and [examples.ipynb Notebook](https://github.com/dynamicdeploy/cloudbulkupload/blob/main/examples.ipynb).

### AWS S3 Usage

#### Import and instantiate a `BulkBoto3` object with your credentials
```python
from cloudbulkupload import BulkBoto3

bulkboto = BulkBoto3(
    endpoint_url="your-endpoint-url",
    aws_access_key_id="your-access-key",
    aws_secret_access_key="your-secret-key",
    max_pool_connections=50,
    verbose=True
)
```

#### Upload a directory to S3
```python
bulkboto.upload_dir_to_storage(
    bucket_name="your-bucket-name",
    local_dir="path/to/local/directory",
    storage_dir="path/in/s3",
    n_threads=50
)
```

#### Download a directory from S3
```python
bulkboto.download_dir_from_storage(
    bucket_name="your-bucket-name",
    storage_dir="path/in/s3",
    local_dir="path/to/local/directory",
    n_threads=50
)
```

### Azure Blob Storage Usage

#### Import and instantiate a `BulkAzureBlob` object
```python
import asyncio
from cloudbulkupload import BulkAzureBlob

async def main():
    azure_client = BulkAzureBlob(
        connection_string="your-azure-connection-string",
        max_concurrent_operations=50,
        verbose=True
    )
    
    # Upload directory
    await azure_client.upload_directory(
        container_name="your-container",
        local_dir="path/to/local/directory",
        storage_dir="path/in/azure"
    )

# Run the async function
asyncio.run(main())
```

#### Bulk upload files
```python
from cloudbulkupload import bulk_upload_blobs

files = ["file1.txt", "file2.txt", "file3.txt"]
await bulk_upload_blobs(
    connection_string="your-connection-string",
    container_name="your-container",
    files_to_upload=files,
    max_concurrent=50,
    verbose=True
)
```

### Google Cloud Storage Usage

#### Import and instantiate a `BulkGoogleStorage` object
```python
import asyncio
from cloudbulkupload import BulkGoogleStorage

async def main():
    google_client = BulkGoogleStorage(
        project_id="your-project-id",
        credentials_path="/path/to/service-account-key.json",  # Optional
        max_concurrent_operations=50,
        verbose=True
    )

    # Upload directory
    await google_client.upload_directory(
        bucket_name="your-bucket",
        local_dir="path/to/local/directory",
        storage_dir="path/in/google-cloud"
    )

# Run the async function
asyncio.run(main())
```

#### Bulk upload files
```python
from cloudbulkupload import google_bulk_upload_blobs

files = ["file1.txt", "file2.txt", "file3.txt"]
await google_bulk_upload_blobs(
    project_id="your-project-id",
    bucket_name="your-bucket",
    files_to_upload=files,
    max_concurrent=50,
    verbose=True
)
```

## Azure Blob Storage

The package now includes comprehensive Azure Blob Storage support with async operations for optimal performance.

### Key Features
- **Async/Await Support**: Full async/await pattern for better performance
- **Concurrency Control**: Configurable concurrency limits with semaphores
- **Progress Tracking**: Built-in progress bars for long operations
- **Error Handling**: Comprehensive error handling and logging
- **Directory Operations**: Upload and download entire directories
- **Bulk Operations**: Convenience functions for bulk uploads/downloads

### Quick Start
```python
import asyncio
from cloudbulkupload import BulkAzureBlob, StorageTransferPath

async def azure_example():
    azure_client = BulkAzureBlob(
        connection_string="your-connection-string",
        max_concurrent_operations=50,
        verbose=True
    )
    
    # Upload files
    upload_paths = [
        StorageTransferPath("file1.txt", "container/file1.txt"),
        StorageTransferPath("file2.txt", "container/file2.txt")
    ]
    
    await azure_client.upload_files("my-container", upload_paths)

asyncio.run(azure_example())
```

For detailed Azure usage, see [AZURE_GUIDE.md](AZURE_GUIDE.md).

## Google Cloud Storage

The package now includes comprehensive Google Cloud Storage support with async operations for optimal performance.

### Key Features
- **Async/Await Support**: Full async/await pattern for better performance
- **Concurrency Control**: Configurable concurrency limits with semaphores
- **Progress Tracking**: Built-in progress bars for long operations
- **Error Handling**: Comprehensive error handling and logging
- **Directory Operations**: Upload and download entire directories
- **Bulk Operations**: Convenience functions for bulk uploads/downloads

### Quick Start
```python
import asyncio
from cloudbulkupload import BulkGoogleStorage, StorageTransferPath

async def google_example():
    google_client = BulkGoogleStorage(
        project_id="your-project-id",
        max_concurrent_operations=50,
        verbose=True
    )

    # Upload files
    upload_paths = [
        StorageTransferPath("file1.txt", "bucket/file1.txt"),
        StorageTransferPath("file2.txt", "bucket/file2.txt")
    ]

    await google_client.upload_files("my-bucket", upload_paths)

asyncio.run(google_example())
```

For detailed Google Cloud usage, see [GOOGLE_CLOUD_GUIDE.md](GOOGLE_CLOUD_GUIDE.md).

## Performance Comparison

The package includes a comprehensive performance comparison system to test AWS S3 vs Azure Blob Storage vs Google Cloud Storage performance.

### Run Performance Tests
```bash
# Install test dependencies
pip install "cloudbulkupload[test]"

# Run Azure vs AWS performance comparison
python run_tests.py --type azure-comparison

# Run three-way performance comparison (AWS, Azure, Google)
python run_tests.py --type three-way-comparison
```

### Test Configuration
- **File Sizes**: 1KB, 10KB, 100KB, 1MB
- **File Counts**: 10, 50, 100 files
- **Concurrency**: 10, 25, 50 operations
- **Metrics**: Upload/download speed, elapsed time

### Expected Benefits
- **Async Operations**: Better resource utilization for Azure and Google Cloud
- **Concurrency Control**: Configurable performance tuning
- **Memory Efficiency**: Reduced memory footprint
- **Scalability**: Better handling of large file sets

For detailed performance analysis, see the generated `performance_comparison_results.csv` and `performance_comparison_three_way_results.csv` files.

## Blog Posts
- [BulkBoto3: Python package for fast and parallel transferring a bulk of files to S3 based on boto3!](http://www.sefidian.com/2022/03/28/bulkboto3-python-package-for-fast-and-parallel-transferring-a-bulk-of-files-to-s3-based-on-boto3/)
- [Deploy Standalone MinIO using Docker Compose on Linux](http://www.sefidian.com/2022/04/08/deploy-standalone-minio-using-docker-compose/).


## Contributing
Any contributions you make are **greatly appreciated**. If you have a suggestion that would make this better, please fork the repo and create a pull request. 
You can also simply open an issue with the tag "enhancement". To contribute to `bulkboto3`, follow these steps:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes and commit them (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

Alternatively, see the GitHub documentation on [creating a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).

## Contributors
Thanks to the following people who have contributed to this project:

* [Amir Masoud Sefidian](https://sefidian.com/) 📖

## Contact
If you want to contact me you can reach me at [a.m.sefidian@gmail.com](mailto:a.m.sefidian@gmail.com).

## License
Distributed under the [MIT](https://choosealicense.com/licenses/mit/) License. See `LICENSE` for more information.



