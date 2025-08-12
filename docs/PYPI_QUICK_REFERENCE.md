# PyPI Quick Reference Card

## 🚀 Quick Publishing Commands

### Build Package
```bash
python -m build
twine check dist/*
```

### Upload to TestPyPI
```bash
twine upload --repository testpypi dist/*
# Username: __token__
# Password: your-testpypi-token
```

### Upload to Main PyPI
```bash
twine upload dist/*
# Username: __token__
# Password: your-main-pypi-token
```

## 📦 Quick Installation Commands

### Basic Installation
```bash
pip install cloudbulkupload
```

### With Test Dependencies
```bash
pip install "cloudbulkupload[test]"
```

### With Development Dependencies
```bash
pip install "cloudbulkupload[dev]"
```

### From Source
```bash
git clone https://github.com/dynamicdeploy/cloudbulkupload.git
cd cloudbulkupload
pip install -e ".[test]"
```

## ✅ Quick Verification

### Test Import
```python
from cloudbulkupload import BulkBoto3, StorageTransferPath
print("✅ Import successful!")
```

### Test Installation
```bash
python -c "import cloudbulkupload; print(cloudbulkupload.__version__)"
```

### Run Tests
```bash
python run_tests.py --type quick
python run_tests.py --type all
```

## 🔧 Configuration Files

### ~/.pypirc
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-main-token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-token
```

## 📋 Version Management

### Update Version
1. Update `pyproject.toml`
2. Update `cloudbulkupload/__init__.py`
3. Update `setup.py` (if used)

### Rebuild and Upload
```bash
rm -rf dist/ build/
python -m build
twine upload dist/*
```

## 🔗 Useful Links

- **TestPyPI**: https://test.pypi.org/project/cloudbulkupload/
- **Main PyPI**: https://pypi.org/project/cloudbulkupload/
- **GitHub**: https://github.com/dynamicdeploy/cloudbulkupload

## 🚨 Common Issues

| Issue | Solution |
|-------|----------|
| Package name exists | Increment version number |
| Authentication failed | Check API token |
| Import error | Reinstall package |
| Build error | Install wheel: `pip install wheel` |
| Test dependencies missing | Install with `[test]` |

## 📝 Usage Example

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
```

---

**For detailed instructions, see**: `PYPI_PUBLISHING_GUIDE.md`
