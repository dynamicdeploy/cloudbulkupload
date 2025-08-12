# Testing Guide for cloudbulkupload

This document provides comprehensive instructions for running the test suite for the `cloudbulkupload` package.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Test Suite Overview](#test-suite-overview)
4. [Running Tests](#running-tests)
5. [Test Types](#test-types)
6. [Performance Testing](#performance-testing)
7. [Comparison Testing](#comparison-testing)
8. [Troubleshooting](#troubleshooting)
9. [Continuous Integration](#continuous-integration)

## Prerequisites

### Required Software
- Python 3.11 or higher
- pip (Python package installer)
- Git (for cloning the repository)

### AWS/S3 Access
- AWS credentials or MinIO credentials
- S3-compatible storage endpoint
- Appropriate permissions for bucket creation/deletion

### System Requirements
- Minimum 2GB RAM
- Stable internet connection (for S3 operations)
- Sufficient disk space for test files

## Environment Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd cloudbulkupload
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Install the package in editable mode with test dependencies
pip install -e ".[test]"

# Or install test dependencies separately
pip install pytest pytest-cov python-dotenv
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:

```bash
# For AWS S3
AWS_ENDPOINT_URL=https://s3.amazonaws.com
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# For MinIO (local development)
AWS_ENDPOINT_URL=http://localhost:9000
AWS_ACCESS_KEY_ID=your_minio_access_key
AWS_SECRET_ACCESS_KEY=your_minio_secret_key
```

### 5. Verify Setup
```bash
# Run quick test to verify setup
python tests/quick_test.py
```

## Test Suite Overview

The test suite consists of several components:

### Core Test Files
- `tests/test_bulkboto3.py` - Main test suite (10 test cases)
- `tests/performance_benchmark.py` - Performance analysis
- `tests/quick_test.py` - Fast validation script
- `tests/without_bulkboto.py` - Regular boto3 comparison
- `tests/comparison_test.py` - cloudbulkupload vs boto3 comparison

### Configuration Files
- `pytest.ini` - pytest configuration
- `run_tests.py` - Test runner script
- `pyproject.toml` - Package configuration with test dependencies
- `tests/test_config.py` - Test configuration and cleanup settings

### Documentation
- `tests/README.md` - Detailed test documentation
- `TESTING.md` - This file
- `TEST_RESULTS.md` - Test results summary
- `test_results.csv` - Detailed test results

## Running Tests

### Method 1: Using the Test Runner Script (Recommended)

The `run_tests.py` script provides an easy way to run different types of tests:

```bash
# Quick validation (fastest)
python run_tests.py --type unit

# Performance tests
python run_tests.py --type performance

# All tests including slow ones
python run_tests.py --type all

# Performance benchmark
python run_tests.py --type benchmark

# Comparison tests (cloudbulkupload vs boto3)
python run_tests.py --type comparison

# With coverage reporting
python run_tests.py --type unit --coverage

# Verbose output
python run_tests.py --type all --verbose
```

### Method 2: Using pytest Directly

```bash
# Run all tests
pytest tests/

# Run only unit tests (exclude slow tests)
pytest tests/ -m "not slow"

# Run only performance tests
pytest tests/ -m "performance"

# Run comparison tests
pytest tests/ -m "comparison"

# Run with coverage
pytest tests/ --cov=bulkboto3 --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_bulkboto3.py

# Run specific test method
pytest tests/test_bulkboto3.py::TestBulkBoto3::test_single_file_upload_performance

# Verbose output
pytest tests/ -v

# Show print statements
pytest tests/ -s
```

### Method 3: Individual Scripts

```bash
# Quick test (fastest validation)
python tests/quick_test.py

# Performance benchmark
python tests/performance_benchmark.py

# Comparison test
python tests/comparison_test.py

# Regular boto3 test
python tests/without_bulkboto.py
```

## Test Types

### 1. Unit Tests
**Purpose**: Verify basic functionality
**Duration**: ~30 seconds
**Command**: `python run_tests.py --type unit`

**Tests Include**:
- Connection testing
- Bucket operations
- Object operations
- Error handling

### 2. Performance Tests
**Purpose**: Measure upload/download speeds
**Duration**: ~2-5 minutes
**Command**: `python run_tests.py --type performance`

**Tests Include**:
- Single file upload performance
- Multiple files upload performance
- Directory upload performance
- Download performance
- Large file upload performance

### 3. Performance Benchmark
**Purpose**: Comprehensive performance analysis
**Duration**: ~5-10 minutes
**Command**: `python run_tests.py --type benchmark`

**Analysis Includes**:
- Different file sizes (1KB to 10MB)
- Different thread counts (1-50)
- Concurrent operations
- Performance recommendations

### 4. Comparison Tests
**Purpose**: Compare cloudbulkupload vs regular boto3
**Duration**: ~3-5 minutes
**Command**: `python run_tests.py --type comparison`

**Comparison Includes**:
- Upload speed comparison
- Thread count impact
- File size impact
- Performance improvement metrics

## Performance Testing

### Understanding Performance Metrics

The tests measure several key metrics:

1. **Upload Time**: Time taken to upload files (seconds)
2. **Upload Speed**: Data transfer rate (MB/s)
3. **Throughput**: Total data transferred per unit time
4. **Efficiency**: Performance improvement over regular boto3

### Performance Test Categories

#### Single File Uploads
- Small files (1KB)
- Medium files (100KB)
- Large files (1MB)
- Extra large files (10MB)

#### Directory Uploads
- Different thread counts (1, 2, 5, 10, 20, 50)
- Mixed file sizes
- Directory structure preservation

#### Concurrent Operations
- Multiple simultaneous uploads
- Upload/download overlap
- Resource utilization

### Interpreting Results

#### Good Performance Indicators
- Upload speeds > 10 MB/s for large files
- Thread count optimization (usually 10-20 threads)
- Consistent performance across multiple runs
- Successful error handling

#### Performance Warnings
- Upload speeds < 1 MB/s
- High variance in timing results
- Failed uploads or timeouts
- Memory or resource exhaustion

## Comparison Testing

### cloudbulkupload vs Regular boto3

The comparison tests measure the performance improvement of cloudbulkupload over regular boto3:

#### Test Scenarios
1. **Single File Uploads**: Compare upload times for different file sizes
2. **Directory Uploads**: Compare bulk upload performance
3. **Thread Scaling**: Measure performance with different thread counts
4. **Resource Usage**: Compare memory and CPU usage

#### Metrics Measured
- **Speedup Factor**: How much faster cloudbulkupload is
- **Efficiency Gain**: Performance improvement percentage
- **Resource Utilization**: Memory and CPU usage comparison
- **Reliability**: Success rate comparison

### Running Comparison Tests

```bash
# Run all comparison tests
python run_tests.py --type comparison

# Run specific comparison test
pytest tests/comparison_test.py::TestComparison::test_upload_speed_comparison

# Run with detailed output
pytest tests/comparison_test.py -v -s
```

## Cleanup Configuration

The test suite includes configurable cleanup options to control what gets deleted after tests. By default, all test data, buckets, and local files are cleaned up.

### Environment Variables

You can control cleanup behavior using environment variables:

```bash
# Disable all cleanup operations
export CLEANUP_ENABLED=false

# Keep test data in buckets (but delete buckets)
export KEEP_TEST_DATA=true

# Keep test buckets (overrides KEEP_TEST_DATA)
export KEEP_BUCKETS=true

# Keep local test files and directories
export KEEP_LOCAL_FILES=true

# Set performance test iterations
export PERFORMANCE_ITERATIONS=5

# Set maximum thread count
export MAX_THREADS=100

# Enable verbose test output
export VERBOSE_TESTS=true
```

### Command Line Options

Use `run_tests.py` with cleanup flags:

```bash
# Keep all test data and buckets
python run_tests.py --keep-data

# Keep only buckets (clean up data)
python run_tests.py --keep-buckets

# Keep only local files (clean up buckets)
python run_tests.py --keep-files

# Disable all cleanup
python run_tests.py --no-cleanup

# Combine with other options
python run_tests.py --type performance --keep-data --verbose
```

### Cleanup Behavior Examples

#### Default Behavior (Clean Everything)
```bash
python run_tests.py --type unit
```
- ✅ Deletes test buckets
- ✅ Deletes uploaded test data
- ✅ Deletes local test files

#### Keep Data for Inspection
```bash
python run_tests.py --type comparison --keep-data
```
- ❌ Keeps test buckets
- ❌ Keeps uploaded test data
- ✅ Deletes local test files

#### Keep Only Local Files
```bash
python run_tests.py --type performance --keep-files
```
- ✅ Deletes test buckets
- ✅ Deletes uploaded test data
- ❌ Keeps local test files

#### Disable All Cleanup
```bash
python run_tests.py --type all --no-cleanup
```
- ❌ Keeps test buckets
- ❌ Keeps uploaded test data
- ❌ Keeps local test files

### Use Cases for Keeping Data

#### Debugging Failed Tests
```bash
# Keep everything to inspect what went wrong
CLEANUP_ENABLED=false python -m pytest tests/test_bulkboto3.py
```

#### Performance Analysis
```bash
# Keep data to analyze upload patterns
python run_tests.py --type performance --keep-data
```

#### Manual Verification
```bash
# Keep buckets to manually verify uploads
python run_tests.py --type unit --keep-buckets
```

#### Development Testing
```bash
# Keep local files for repeated testing
python run_tests.py --type quick --keep-files
```

## Troubleshooting

### Common Issues and Solutions

#### 1. AWS Credentials Not Found
**Error**: `ValueError: AWS credentials not found in .env file`
**Solution**: 
- Check that `.env` file exists in project root
- Verify credentials are correctly formatted
- Ensure no extra spaces or quotes

#### 2. Connection Errors
**Error**: `Cannot connect to object storage`
**Solution**:
- Verify endpoint URL is correct
- Check network connectivity
- Ensure S3 service is running (for MinIO)

#### 3. Permission Errors
**Error**: `Access Denied` or `Forbidden`
**Solution**:
- Verify AWS credentials have appropriate permissions
- Check bucket name availability
- Ensure credentials are not expired

#### 4. Slow Test Performance
**Issue**: Tests taking too long
**Solution**:
- Use `-m "not slow"` to skip slow tests
- Reduce file sizes in test configuration
- Check network bandwidth

#### 5. Memory Issues
**Error**: `MemoryError` or out of memory
**Solution**:
- Reduce test file sizes
- Close other applications
- Increase system memory if possible

### Debug Mode

For detailed debugging:

```bash
# Run with maximum verbosity
pytest tests/ -v -s --tb=long

# Run specific test with debug output
pytest tests/test_bulkboto3.py::TestBulkBoto3::test_connection -v -s

# Check environment variables
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('AWS_ENDPOINT_URL:', os.getenv('AWS_ENDPOINT_URL'))"
```

### Test Data Cleanup

If tests fail and leave test data:

```bash
# Clean up test buckets (replace with your bucket names)
aws s3 rb s3://test-bulkboto3-bucket --force
aws s3 rb s3://performance-benchmark-bucket --force
aws s3 rb s3://without-bulkboto --force

# Clean up local test directories
rm -rf /tmp/bulkboto3_test_*
rm -rf /tmp/performance_benchmark_*
```

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[test]"
    
    - name: Run quick tests
      run: python tests/quick_test.py
      env:
        AWS_ENDPOINT_URL: ${{ secrets.AWS_ENDPOINT_URL }}
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    
    - name: Run unit tests
      run: python run_tests.py --type unit --coverage
      env:
        AWS_ENDPOINT_URL: ${{ secrets.AWS_ENDPOINT_URL }}
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### Local CI Setup

For local continuous testing:

```bash
# Watch for file changes and run tests
pip install watchdog
watchmedo auto-restart --patterns="*.py" --recursive -- python run_tests.py --type unit
```

## Best Practices

### 1. Regular Testing
- Run quick tests before committing code
- Run full test suite before releases
- Monitor performance trends over time

### 2. Test Data Management
- Use temporary directories for test files
- Clean up test buckets after tests
- Avoid using production data in tests

### 3. Performance Monitoring
- Track performance metrics over time
- Set performance baselines
- Alert on performance regressions

### 4. Documentation
- Update test documentation when adding new tests
- Document performance expectations
- Keep troubleshooting guides current

## Support

For issues with the test suite:

1. Check the troubleshooting section above
2. Review the test logs for specific error messages
3. Verify your environment setup
4. Check the project issues page
5. Create a new issue with detailed information

---

**Last Updated**: August 2024
**Test Suite Version**: 1.0.0
