# 📦 Publishing Scripts for cloudbulkupload

This directory contains automated scripts for publishing the `cloudbulkupload` package to TestPyPI and PyPI.

## 🚀 Available Scripts

### 1. `publish_testpypi.sh` - TestPyPI Publishing
Publishes the package to TestPyPI for testing before production release.

### 2. `publish_pypi.sh` - PyPI Publishing
Publishes the package to PyPI (production) for public distribution.

## 📋 Prerequisites

### Required Tools
- **Python 3.11+**
- **pip**
- **twine** (will be installed automatically if missing)
- **Virtual environment** (must be activated)

### Required Files
- **`.pypirc`** - Configuration file with your PyPI credentials

## 🔧 Setup

### 1. Create `.pypirc` Configuration File

Create a `.pypirc` file in the project root with your PyPI credentials:

```ini
[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = your-testpypi-token

[pypi]
username = __token__
password = your-pypi-token
```

### 2. Get PyPI Tokens

#### TestPyPI Token
1. Go to [TestPyPI](https://test.pypi.org/)
2. Create an account or log in
3. Go to Account Settings → API tokens
4. Create a new token with "Entire account" scope
5. Copy the token (starts with `pypi-`)

#### PyPI Token
1. Go to [PyPI](https://pypi.org/)
2. Create an account or log in
3. Go to Account Settings → API tokens
4. Create a new token with "Entire account" scope
5. Copy the token (starts with `pypi-`)

### 3. Activate Virtual Environment

```bash
source venv/bin/activate
```

## 🎯 Usage

### Publishing to TestPyPI (Recommended First Step)

```bash
./publish_testpypi.sh
```

**What this script does:**
1. ✅ Checks virtual environment is activated
2. ✅ Verifies all dependencies are installed
3. ✅ Cleans previous builds
4. ✅ Builds the package
5. ✅ Validates package with twine
6. ✅ Displays package information
7. ✅ Prompts for confirmation
8. ✅ Publishes to TestPyPI
9. ✅ Provides installation instructions

### Publishing to PyPI (Production)

```bash
./publish_pypi.sh
```

**What this script does:**
1. ✅ Checks virtual environment is activated
2. ✅ Verifies all dependencies are installed
3. ✅ Cleans previous builds
4. ✅ Builds the package
5. ✅ Validates package with twine
6. ✅ Runs basic tests
7. ✅ Checks version consistency
8. ✅ Verifies version doesn't already exist on PyPI
9. ✅ Displays package information
10. ✅ **Double confirmation** for production publishing
11. ✅ Publishes to PyPI
12. ✅ Provides next steps

## 🔍 Script Features

### Safety Checks
- **Virtual Environment**: Ensures virtual environment is activated
- **Dependencies**: Checks and installs required tools
- **Version Consistency**: Verifies version in `pyproject.toml` matches `__init__.py`
- **Version Existence**: Checks if version already exists on PyPI
- **Package Validation**: Uses twine to validate package before upload

### Error Handling
- **Exit on Error**: Scripts stop on first error
- **Colored Output**: Clear status messages with colors
- **Detailed Error Messages**: Helpful error descriptions
- **Graceful Failures**: Proper cleanup on errors

### User Confirmation
- **TestPyPI**: Single confirmation prompt
- **PyPI**: Double confirmation for production safety
- **Cancellation**: Graceful handling of user cancellation

## 📊 Package Information Display

Both scripts display:
- Package name and version
- Author information
- Built package files
- File sizes and details

## 🧪 Testing After Publishing

### TestPyPI Installation
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ cloudbulkupload
```

### PyPI Installation
```bash
pip install cloudbulkupload
```

## 🚨 Important Notes

### Version Management
- **Always increment version** before publishing
- **Version consistency** is automatically checked
- **Duplicate version prevention** on PyPI

### Production Publishing
- **TestPyPI first**: Always test on TestPyPI before PyPI
- **Double confirmation**: PyPI script requires double confirmation
- **Irreversible**: PyPI publishing cannot be undone
- **Global availability**: Package becomes available worldwide

### Security
- **Never commit `.pypirc`**: Add to `.gitignore`
- **Use tokens**: Use API tokens instead of passwords
- **Limited scope**: Use minimal required permissions

## 🔧 Troubleshooting

### Common Issues

#### "Virtual environment is not activated"
```bash
source venv/bin/activate
```

#### ".pypirc file not found"
Create the `.pypirc` file with your credentials (see Setup section)

#### "Version already exists on PyPI"
Increment the version number in `pyproject.toml` and `__init__.py`

#### "Package validation failed"
Check for syntax errors or missing files in the package

#### "Authentication failed"
Verify your PyPI tokens are correct in `.pypirc`

### Manual Publishing (if scripts fail)

#### TestPyPI
```bash
python -m build
twine check dist/*
twine upload --repository testpypi dist/*
```

#### PyPI
```bash
python -m build
twine check dist/*
twine upload dist/*
```

## 📈 Workflow

### Recommended Publishing Workflow

1. **Develop and Test**
   ```bash
   # Run tests
   python run_tests.py --type all
   ```

2. **Update Version**
   ```bash
   # Edit pyproject.toml and __init__.py
   # Increment version number
   ```

3. **TestPyPI Publishing**
   ```bash
   ./publish_testpypi.sh
   ```

4. **Test Installation**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ cloudbulkupload
   ```

5. **PyPI Publishing**
   ```bash
   ./publish_pypi.sh
   ```

6. **Verify and Document**
   - Check PyPI page
   - Update documentation
   - Create GitHub release

## 🎉 Success Indicators

### TestPyPI Success
- ✅ Package appears on https://test.pypi.org/project/cloudbulkupload/
- ✅ Installation works with test index
- ✅ All functionality works correctly

### PyPI Success
- ✅ Package appears on https://pypi.org/project/cloudbulkupload/
- ✅ Installation works with standard pip
- ✅ Package is available worldwide

---

**Last Updated**: August 12, 2025  
**Package Version**: 2.0.0
