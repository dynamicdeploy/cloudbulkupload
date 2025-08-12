# Change Log:

**v2.0.0:**
- **🚀 Major Release: Multi-Cloud Support**
- **🆕 Google Cloud Storage Support**:
  - Complete async Google Cloud Storage implementation
  - Hybrid approach with Google's Transfer Manager for maximum performance
  - Support for service account authentication (file and JSON string)
  - Application Default Credentials support
  - Comprehensive bucket and blob management operations
- **🔄 Enhanced Azure Blob Storage**:
  - Improved async operations with better error handling
  - Fixed download stream handling
  - Enhanced progress tracking and logging
- **🧪 Comprehensive Testing Suite**:
  - Complete test suite for all three cloud providers
  - Performance comparison tools (AWS vs Azure vs Google Cloud)
  - Automated test runners with different test types
  - Performance metrics and CSV result generation
- **📚 Enhanced Documentation**:
  - Complete rewrite of README.md with multi-cloud focus
  - Comprehensive guides for each cloud provider
  - Implementation summaries and testing documentation
  - PyPI publishing guides and quick references
- **🔧 Improved Architecture**:
  - Unified API across all cloud providers
  - Better error handling and logging
  - Configurable concurrency and performance tuning
  - Progress tracking for all operations
- **📦 Package Improvements**:
  - Updated dependencies for all cloud providers
  - Better package structure and organization
  - Comprehensive optional dependencies for testing
  - Improved build configuration

**v1.1.3:**
- Add examples as a Jupyter Notebook file.

**v1.1.2:**
- Add Standalone MinIO deployment link to README.md.
- Add blog posts to README.md.

**v1.1.1:**
- Fix licence badge.

**v1.1.0:**
- Change package name to `bulkboto3`

**v1.0.3:**
- Add use case of transferring arbitrary files to S3

**v1.0.2:**
- Fix `find_namespace_packages` argument in `setup.py`

**v1.0.1:**
- Fix links for PyPI

**v1.0.0:**
- Initial release
- Features:
  - Multi-thread uploading/downloading of a directory (keeping the directory structure) to/from S3 object storage
  - Deleting all objects of an S3 bucket
  - Checking the existence of an object on the S3 bucket
  - Listing all objects on an S3 bucket
  - Creating a new S3 bucket on the object storage