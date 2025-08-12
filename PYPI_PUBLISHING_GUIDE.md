# PyPI Publishing and Installation Guide for cloudbulkupload

This document provides detailed step-by-step instructions for publishing the `cloudbulkupload` package to PyPI and installing it.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Package Preparation](#package-preparation)
3. [PyPI Account Setup](#pypi-account-setup)
4. [TestPyPI Publishing](#testpypi-publishing)
5. [Main PyPI Publishing](#main-pypi-publishing)
6. [Package Installation](#package-installation)
7. [Verification and Testing](#verification-and-testing)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- Python 3.11 or higher
- pip (Python package installer)
- Git (for version control)

### Required Python Packages
```bash
pip install build twine
```

### Project Structure
Ensure your project has the following structure:
```
cloudbulkupload/
├── cloudbulkupload/
│   ├── __init__.py
│   ├── bulkboto3.py
│   ├── exceptions.py
│   └── transfer_path.py
├── tests/
├── pyproject.toml
├── setup.py
├── README.md
└── LICENSE
```

## Package Preparation

### Step 1: Verify Package Configuration

Check that your `pyproject.toml` contains the correct package information:

```toml
[project]
name = "cloudbulkupload"
version = "1.1.3"
description = "Python package for fast and parallel transferring a bulk of files to S3 based on boto3"
readme = "README.md"
license = "MIT"
authors = [
    {name = "Dynamic Deploy. Credit: Amir Masoud Sefidian", email = "dynamicdeploy@gmail.com"}
]
requires-python = ">=3.11.0"
dependencies = [
    "boto3>=1.21.26",
    "tqdm",
]
```

### Step 2: Build the Package

```bash
# Activate your virtual environment
source venv/bin/activate

# Build the package
python -m build
```

This creates two files in the `dist/` directory:
- `cloudbulkupload-1.1.3.tar.gz` (source distribution)
- `cloudbulkupload-1.1.3-py3-none-any.whl` (wheel distribution)

### Step 3: Validate the Package

```bash
# Check the built package for issues
twine check dist/*
```

Expected output:
```
Checking dist/cloudbulkupload-1.1.3-py3-none-any.whl: PASSED
Checking dist/cloudbulkupload-1.1.3.tar.gz: PASSED
```

## PyPI Account Setup

### Step 1: Create PyPI Account

1. **Visit PyPI**: Go to [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. **Sign Up**: Create a new account with your email
3. **Verify Email**: Check your email and click the verification link
4. **Enable 2FA**: Enable two-factor authentication for security

### Step 2: Create TestPyPI Account

1. **Visit TestPyPI**: Go to [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/)
2. **Sign Up**: Create a new account (can use same email as PyPI)
3. **Verify Email**: Check your email and click the verification link

### Step 3: Generate API Tokens

#### For TestPyPI:
1. Go to [https://test.pypi.org/manage/account/token/](https://test.pypi.org/manage/account/token/)
2. Click "Add API token"
3. **Token name**: `cloudbulkupload-test-token`
4. **Scope**: "Entire account (all projects)"
5. Copy the generated token (starts with `pypi-...`)

#### For Main PyPI:
1. Go to [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
2. Click "Add API token"
3. **Token name**: `cloudbulkupload-prod-token`
4. **Scope**: "Entire account (all projects)"
5. Copy the generated token (starts with `pypi-...`)

### Step 4: Configure Authentication (Optional)

Create a `~/.pypirc` file for easier authentication:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-main-pypi-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-testpypi-token-here
```

## TestPyPI Publishing

### Step 1: Upload to TestPyPI

```bash
# Activate virtual environment
source venv/bin/activate

# Upload to TestPyPI
twine upload --repository testpypi dist/*
```

When prompted:
- **Username**: `__token__`
- **Password**: Your TestPyPI API token

Expected output:
```
Uploading distributions to https://test.pypi.org/legacy/
Enter your API token: 
Uploading cloudbulkupload-1.1.3-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 27.0/27.0 kB • 00:00 • 8.0 MB/s
Uploading cloudbulkupload-1.1.3.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 35.7/35.7 kB • 00:00 • 17.3 MB/s

View at:
https://test.pypi.org/project/cloudbulkupload/1.1.3/
```

### Step 2: Test Installation from TestPyPI

```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ cloudbulkupload

# Test import
python -c "from cloudbulkupload import BulkBoto3, StorageTransferPath; print('✅ TestPyPI package works!')"
```

### Step 3: Verify TestPyPI Package

1. **Visit**: [https://test.pypi.org/project/cloudbulkupload/](https://test.pypi.org/project/cloudbulkupload/)
2. **Check**: Package metadata, description, and files
3. **Test**: Run your test suite with the TestPyPI version

## Main PyPI Publishing

### Step 1: Check Package Name Availability

Before publishing, ensure the package name is available:
1. Visit [https://pypi.org/project/cloudbulkupload/](https://pypi.org/project/cloudbulkupload/)
2. If the package exists, you'll need to use a different name or version

### Step 2: Upload to Main PyPI

```bash
# Activate virtual environment
source venv/bin/activate

# Upload to main PyPI
twine upload dist/*
```

When prompted:
- **Username**: `__token__`
- **Password**: Your main PyPI API token

Expected output:
```
Uploading distributions to https://upload.pypi.org/legacy/
Enter your API token: 
Uploading cloudbulkupload-1.1.3-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 27.0/27.0 kB • 00:00 • 8.0 MB/s
Uploading cloudbulkupload-1.1.3.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 35.7/35.7 kB • 00:00 • 17.3 MB/s
```

### Step 3: Verify PyPI Publication

1. **Visit**: [https://pypi.org/project/cloudbulkupload/](https://pypi.org/project/cloudbulkupload/)
2. **Check**: Package page, metadata, and download statistics
3. **Wait**: It may take a few minutes for the package to be fully indexed

## Package Installation

### Method 1: Basic Installation

```bash
# Install the package
pip install cloudbulkupload

# Verify installation
python -c "import cloudbulkupload; print(cloudbulkupload.__version__)"
```

### Method 2: Installation with Test Dependencies

```bash
# Install with test dependencies
pip install "cloudbulkupload[test]"

# This includes: pytest, pytest-cov, python-dotenv
```

### Method 3: Installation with Development Dependencies

```bash
# Install with development dependencies
pip install "cloudbulkupload[dev]"

# This includes: isort, black
```

### Method 4: Installation from Source

```bash
# Clone the repository
git clone https://github.com/dynamicdeploy/cloudbulkupload.git
cd cloudbulkupload

# Install in editable mode
pip install -e .

# Install with test dependencies
pip install -e ".[test]"
```

## Verification and Testing

### Step 1: Basic Import Test

```python
# Test basic import
from cloudbulkupload import BulkBoto3, StorageTransferPath
print("✅ Import successful!")

# Check available classes
print(f"BulkBoto3: {BulkBoto3}")
print(f"StorageTransferPath: {StorageTransferPath}")
```

### Step 2: Functionality Test

```python
import os
from dotenv import load_dotenv
from cloudbulkupload import BulkBoto3, StorageTransferPath

# Load environment variables
load_dotenv()

# Initialize BulkBoto3
bulkboto = BulkBoto3(
    endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:9000"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    max_pool_connections=50,
    verbose=False
)

print("✅ BulkBoto3 initialized successfully!")

# Test StorageTransferPath
path = StorageTransferPath(
    local_path="test.txt",
    storage_path="test/test.txt"
)
print("✅ StorageTransferPath created successfully!")
```

### Step 3: Run Test Suite

```bash
# Run quick test
python tests/quick_test.py

# Run all tests
python run_tests.py --type all

# Run with cleanup options
python run_tests.py --type quick --keep-data
```

### Step 4: Performance Test

```bash
# Run performance benchmark
python run_tests.py --type benchmark

# Run comparison tests
python run_tests.py --type comparison
```

## Usage Examples

### Basic Usage

```python
from cloudbulkupload import BulkBoto3, StorageTransferPath

# Initialize
bulkboto = BulkBoto3(
    endpoint_url="your-endpoint",
    aws_access_key_id="your-key",
    aws_secret_access_key="your-secret"
)

# Upload directory
bulkboto.upload_dir_to_storage(
    bucket_name="my-bucket",
    local_dir="local/path",
    storage_dir="s3/path",
    n_threads=50
)

# Upload specific files
upload_paths = [
    StorageTransferPath(
        local_path="file1.txt",
        storage_path="s3/file1.txt"
    ),
    StorageTransferPath(
        local_path="file2.txt",
        storage_path="s3/file2.txt"
    )
]
bulkboto.upload(bucket_name="my-bucket", upload_paths=upload_paths)
```

### Advanced Usage

```python
# Download directory
bulkboto.download_dir_from_storage(
    bucket_name="my-bucket",
    storage_dir="s3/path",
    local_dir="local/download",
    n_threads=50
)

# Check if file exists
exists = bulkboto.check_object_exists(
    bucket_name="my-bucket",
    object_path="s3/file.txt"
)

# List objects
objects = bulkboto.list_objects(
    bucket_name="my-bucket",
    storage_dir="s3/path"
)

# Empty bucket
bulkboto.empty_bucket("my-bucket")
```

## Troubleshooting

### Common Issues

#### 1. Package Name Already Exists
**Error**: `HTTPError: 400 Client Error: File already exists.`
**Solution**: Increment the version number in `pyproject.toml` and `cloudbulkupload/__init__.py`

#### 2. Authentication Failed
**Error**: `HTTPError: 401 Client Error: Unauthorized`
**Solution**: 
- Check your API token is correct
- Ensure you're using `__token__` as username
- Verify the token has the correct scope

#### 3. Import Error After Installation
**Error**: `ModuleNotFoundError: No module named 'cloudbulkupload'`
**Solution**:
```bash
# Reinstall the package
pip uninstall cloudbulkupload
pip install cloudbulkupload

# Check installation
pip show cloudbulkupload
```

#### 4. Build Errors
**Error**: `error: invalid command 'bdist_wheel'`
**Solution**:
```bash
pip install wheel
python -m build
```

#### 5. Test Dependencies Missing
**Error**: `ModuleNotFoundError: No module named 'pytest'`
**Solution**:
```bash
pip install "cloudbulkupload[test]"
```

### Version Management

#### Updating Package Version

1. **Update version in files**:
   ```bash
   # Update pyproject.toml
   # Update cloudbulkupload/__init__.py
   # Update setup.py (if using it)
   ```

2. **Rebuild package**:
   ```bash
   rm -rf dist/ build/
   python -m build
   ```

3. **Upload new version**:
   ```bash
   twine upload dist/*
   ```

### Security Best Practices

1. **Use API Tokens**: Never use your PyPI password directly
2. **Scope Tokens**: Use project-specific tokens when possible
3. **Rotate Tokens**: Regularly update your API tokens
4. **Secure Storage**: Store tokens securely (environment variables or keyring)
5. **2FA**: Always enable two-factor authentication on PyPI

## Maintenance

### Regular Tasks

1. **Monitor Downloads**: Check [https://pypi.org/project/cloudbulkupload/](https://pypi.org/project/cloudbulkupload/) for download statistics
2. **Update Dependencies**: Regularly update package dependencies
3. **Security Updates**: Monitor for security vulnerabilities
4. **User Feedback**: Respond to issues and feature requests

### Updating the Package

1. **Make Changes**: Update code, tests, and documentation
2. **Update Version**: Increment version number
3. **Test Locally**: Run all tests before publishing
4. **Build Package**: `python -m build`
5. **Upload**: `twine upload dist/*`
6. **Verify**: Test installation and functionality

## Additional Resources

- **PyPI Documentation**: [https://packaging.python.org/guides/distributing-packages-using-setuptools/](https://packaging.python.org/guides/distributing-packages-using-setuptools/)
- **TestPyPI**: [https://test.pypi.org/](https://test.pypi.org/)
- **PyPI**: [https://pypi.org/](https://pypi.org/)
- **Python Packaging Authority**: [https://www.pypa.io/](https://www.pypa.io/)

---

**Last Updated**: August 2024  
**Package Version**: 1.1.3  
**Python Version**: 3.11+
