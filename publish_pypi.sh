#!/bin/bash

# PyPI Publishing Script for cloudbulkupload
# This script builds and publishes the package to PyPI (production)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if virtual environment is activated
check_venv() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_error "Virtual environment is not activated!"
        print_status "Please activate your virtual environment first:"
        echo "  source venv/bin/activate"
        exit 1
    fi
    print_success "Virtual environment is active: $VIRTUAL_ENV"
}

# Function to check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command_exists python; then
        print_error "Python is not installed or not in PATH"
        exit 1
    fi
    
    if ! command_exists pip; then
        print_error "pip is not installed or not in PATH"
        exit 1
    fi
    
    if ! command_exists twine; then
        print_warning "twine is not installed. Installing now..."
        pip install twine
    fi
    
    print_success "All dependencies are available"
}

# Function to clean previous builds
clean_builds() {
    print_status "Cleaning previous builds..."
    
    if [ -d "build" ]; then
        rm -rf build/
        print_success "Removed build directory"
    fi
    
    if [ -d "dist" ]; then
        rm -rf dist/
        print_success "Removed dist directory"
    fi
    
    if [ -d "*.egg-info" ]; then
        rm -rf *.egg-info/
        print_success "Removed egg-info directories"
    fi
}

# Function to build the package
build_package() {
    print_status "Building package..."
    
    # Build the package
    python -m build
    
    if [ $? -eq 0 ]; then
        print_success "Package built successfully"
    else
        print_error "Package build failed"
        exit 1
    fi
}

# Function to check package with twine
check_package() {
    print_status "Checking package with twine..."
    
    twine check dist/*
    
    if [ $? -eq 0 ]; then
        print_success "Package validation passed"
    else
        print_error "Package validation failed"
        exit 1
    fi
}

# Function to run tests before publishing
run_tests() {
    print_status "Running tests before publishing..."
    
    # Check if tests directory exists
    if [ -d "tests" ]; then
        # Run basic import tests
        python -c "
import cloudbulkupload
from cloudbulkupload import BulkBoto3, BulkAzureBlob, BulkGoogleStorage, StorageTransferPath
print('✅ All imports successful')
print(f'Version: {cloudbulkupload.__version__}')
print(f'Author: {cloudbulkupload.__author__}')
"
        
        if [ $? -eq 0 ]; then
            print_success "Basic tests passed"
        else
            print_error "Basic tests failed"
            exit 1
        fi
    else
        print_warning "No tests directory found, skipping tests"
    fi
}

# Function to check version consistency
check_version_consistency() {
    print_status "Checking version consistency..."
    
    # Get version from pyproject.toml
    PYPROJECT_VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
    
    # Get version from __init__.py
    INIT_VERSION=$(python -c "import cloudbulkupload; print(cloudbulkupload.__version__)")
    
    if [ "$PYPROJECT_VERSION" = "$INIT_VERSION" ]; then
        print_success "Version consistency check passed: $PYPROJECT_VERSION"
    else
        print_error "Version mismatch detected!"
        echo "  pyproject.toml: $PYPROJECT_VERSION"
        echo "  __init__.py: $INIT_VERSION"
        exit 1
    fi
}

# Function to check if version already exists on PyPI
check_version_exists() {
    print_status "Checking if version already exists on PyPI..."
    
    VERSION=$(python -c "import cloudbulkupload; print(cloudbulkupload.__version__)")
    
    # Check if version exists on PyPI specifically (not TestPyPI)
    PYPI_VERSIONS=$(pip index versions cloudbulkupload --index-url https://pypi.org/simple/ 2>/dev/null | grep "Available versions:" -A 10 | grep -E "^[[:space:]]*[0-9]+\.[0-9]+\.[0-9]+" | tr -d ' ')
    
    if [ -z "$PYPI_VERSIONS" ]; then
        print_success "Version $VERSION is not yet published on PyPI (no existing versions found)"
    elif echo "$PYPI_VERSIONS" | grep -q "^$VERSION$"; then
        print_error "Version $VERSION already exists on PyPI!"
        print_status "Please increment the version number before publishing."
        exit 1
    else
        print_success "Version $VERSION is not yet published on PyPI"
        print_status "Available versions on PyPI: $PYPI_VERSIONS"
    fi
}

# Function to publish to PyPI
publish_to_pypi() {
    print_status "Publishing to PyPI..."
    
    # Check if .pypirc exists
    if [ ! -f ".pypirc" ]; then
        print_error ".pypirc file not found!"
        print_status "Please create a .pypirc file with your PyPI credentials:"
        echo ""
        echo "[pypi]"
        echo "username = __token__"
        echo "password = your-pypi-token"
        echo ""
        exit 1
    fi
    
    # Upload to PyPI
    twine upload dist/*
    
    if [ $? -eq 0 ]; then
        print_success "Package published to PyPI successfully!"
        print_status "Package URL: https://pypi.org/project/cloudbulkupload/"
    else
        print_error "Failed to publish to PyPI"
        exit 1
    fi
}

# Function to display package information
display_package_info() {
    print_status "Package Information:"
    echo "  Name: cloudbulkupload"
    echo "  Version: $(python -c "import cloudbulkupload; print(cloudbulkupload.__version__)")"
    echo "  Author: $(python -c "import cloudbulkupload; print(cloudbulkupload.__author__)")"
    echo ""
    
    print_status "Built packages:"
    ls -la dist/
    echo ""
}

# Function to display final instructions
display_final_instructions() {
    echo ""
    print_success "🎉 PyPI publishing completed successfully!"
    echo ""
    print_status "Next steps:"
    echo "  1. Verify the package on PyPI: https://pypi.org/project/cloudbulkupload/"
    echo "  2. Test installation: pip install cloudbulkupload"
    echo "  3. Update documentation if needed"
    echo "  4. Create a GitHub release"
    echo ""
    print_status "Package is now available for installation:"
    echo "  pip install cloudbulkupload"
}

# Main execution
main() {
    echo "🚀 PyPI Publishing Script for cloudbulkupload"
    echo "=============================================="
    echo ""
    
    # Check if we're in the right directory
    if [ ! -f "pyproject.toml" ]; then
        print_error "pyproject.toml not found. Please run this script from the project root directory."
        exit 1
    fi
    
    # Run all checks and steps
    check_venv
    check_dependencies
    clean_builds
    build_package
    check_package
    run_tests
    check_version_consistency
    check_version_exists
    display_package_info
    
    # Display warning about production publishing
    echo ""
    print_warning "⚠️  WARNING: You are about to publish to PyPI (production)!"
    print_warning "This will make the package available to all users worldwide."
    echo ""
    
    # Ask for confirmation before publishing
    read -p "Are you absolutely sure you want to publish to PyPI? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Double confirmation for production
        echo ""
        print_warning "⚠️  FINAL WARNING: This will publish to production PyPI!"
        read -p "Type 'YES' to confirm: " -r
        echo ""
        
        if [[ $REPLY == "YES" ]]; then
            publish_to_pypi
            display_final_instructions
        else
            print_warning "Publishing cancelled by user"
            print_status "Package is built and ready for manual publishing"
        fi
    else
        print_warning "Publishing cancelled by user"
        print_status "Package is built and ready for manual publishing"
    fi
}

# Run main function
main "$@"
