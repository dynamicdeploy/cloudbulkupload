# Test Suite for cloudbulkupload

This directory contains comprehensive tests for the `cloudbulkupload` package, including performance benchmarking and upload speed measurements.

## Test Structure

- `test_bulkboto3.py` - Main test suite with unit and performance tests
- `performance_benchmark.py` - Dedicated performance benchmarking script
- `__init__.py` - Package initialization

## Prerequisites

1. **AWS Credentials**: Create a `.env` file in the project root with your AWS credentials:
   ```
   AWS_ENDPOINT_URL=http://localhost:9000  # or your S3 endpoint
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   ```

2. **Test Dependencies**: Install test dependencies:
   ```bash
   pip install -e .[test]
   ```

## Running Tests

### Using the Test Runner Script

The easiest way to run tests is using the `run_tests.py` script:

```bash
# Run unit tests only (fast)
python run_tests.py --type unit

# Run performance tests
python run_tests.py --type performance

# Run all tests
python run_tests.py --type all

# Run performance benchmark
python run_tests.py --type benchmark

# Run with coverage reporting
python run_tests.py --type unit --coverage

# Run in verbose mode
python run_tests.py --type all --verbose
```

### Using pytest directly

```bash
# Run all tests
pytest tests/

# Run only unit tests (exclude slow tests)
pytest tests/ -m "not slow"

# Run only performance tests
pytest tests/ -m "performance"

# Run with coverage
pytest tests/ --cov=bulkboto3 --cov-report=html

# Run specific test file
pytest tests/test_bulkboto3.py::TestBulkBoto3::test_single_file_upload_performance
```

### Running Performance Benchmark

```bash
# Run the comprehensive performance benchmark
python tests/performance_benchmark.py
```

## Test Categories

### Unit Tests
- Connection testing
- Bucket operations
- Object operations
- Error handling

### Performance Tests
- Single file upload performance
- Multiple files upload performance
- Directory upload performance with different thread counts
- Download performance
- Large file upload performance
- Concurrent operations

### Performance Benchmark
The performance benchmark provides detailed analysis of:
- Upload speeds for different file sizes
- Performance with different thread counts
- Concurrent upload performance
- Speed comparisons and recommendations

## Test Output

### Performance Test Results
Performance tests output timing information:
```
Single file upload time: 0.245 seconds
Multiple files upload time: 1.234 seconds
Directory upload with 10 threads: 0.567 seconds
Upload speed: 15.67 MB/s
```

### Benchmark Report
The benchmark generates a comprehensive report:
```
============================================================
PERFORMANCE BENCHMARK REPORT
============================================================

1. SINGLE FILE UPLOAD PERFORMANCE:
----------------------------------------
   small:    2.45 MB/s ( 0.001s)
  medium:   12.34 MB/s ( 0.008s)
   large:   25.67 MB/s ( 0.039s)
  xlarge:   45.89 MB/s ( 0.218s)

2. DIRECTORY UPLOAD PERFORMANCE:
----------------------------------------
Threads | Time (s) | Speed (MB/s) | Objects
----------------------------------------
      1 |    2.345 |        12.34 |      54
      5 |    1.234 |        23.45 |      54
     10 |    0.987 |        29.34 |      54
     20 |    0.876 |        33.12 |      54
     50 |    0.823 |        35.23 |      54

3. CONCURRENT UPLOAD PERFORMANCE:
----------------------------------------
Workers | Total Time (s) | Speed (MB/s) | Success Rate
----------------------------------------
      1 |          1.234 |        12.34 |       50/50
      2 |          0.987 |        15.45 |       50/50
      5 |          0.654 |        23.34 |       50/50
     10 |          0.543 |        28.12 |       50/50

4. PERFORMANCE RECOMMENDATIONS:
----------------------------------------
• Optimal thread count for directory uploads: 50
• Optimal worker count for concurrent uploads: 10
• Directory uploads are 1.4x faster than single file uploads
```

## Environment Variables

The tests use the following environment variables from your `.env` file:

- `AWS_ENDPOINT_URL` - S3 endpoint URL (default: http://localhost:9000)
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key

## Test Data

The tests automatically create temporary test files of various sizes:
- Small files (1KB)
- Medium files (100KB)
- Large files (1MB)
- Extra large files (10MB)
- Multiple small files for bulk testing

All test data is cleaned up automatically after tests complete.

## Troubleshooting

### Common Issues

1. **AWS Credentials Not Found**
   - Ensure your `.env` file exists and contains valid credentials
   - Check that the credentials have appropriate S3 permissions

2. **Connection Errors**
   - Verify your S3 endpoint is accessible
   - Check network connectivity
   - Ensure the endpoint URL is correct

3. **Permission Errors**
   - Ensure your AWS credentials have bucket creation/deletion permissions
   - Check that the test bucket name is available

4. **Slow Tests**
   - Performance tests can take time, especially with large files
   - Use `-m "not slow"` to skip slow tests during development

### Debug Mode

Run tests with verbose output for debugging:
```bash
pytest tests/ -v -s
```

## Contributing

When adding new tests:
1. Follow the existing naming conventions
2. Add appropriate markers (`@pytest.mark.slow`, `@pytest.mark.performance`)
3. Include performance measurements where relevant
4. Ensure proper cleanup in `tearDown` methods
5. Add docstrings explaining what the test does
