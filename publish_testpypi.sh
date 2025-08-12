#!/bin/bash

# TestPyPI Publishing Script for cloudbulkupload
# This script builds and publishes the package to TestPyPI for testing

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

# Function to test package installation
test_installation() {
    print_status "Testing package installation..."
    
    # Create a temporary directory for testing
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # Create a test virtual environment
    python -m venv test_env
    source test_env/bin/activate
    
    # Install the package
    pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ cloudbulkupload
    
    if [ $? -eq 0 ]; then
        print_success "Package installation test passed"
    else
        print_error "Package installation test failed"
        cd - > /dev/null
        rm -rf "$TEMP_DIR"
        exit 1
    fi
    
    # Test import
    python -c "import cloudbulkupload; print(f'✅ Package imported successfully: {cloudbulkupload.__version__}')"
    
    # Cleanup
    deactivate
    cd - > /dev/null
    rm -rf "$TEMP_DIR"
}

# Function to publish to TestPyPI
publish_to_testpypi() {
    print_status "Publishing to TestPyPI..."
    
    # Check if .pypirc exists
    if [ ! -f ".pypirc" ]; then
        print_error ".pypirc file not found!"
        print_status "Please create a .pypirc file with your TestPyPI credentials:"
        echo ""
        echo "[testpypi]"
        echo "repository = https://test.pypi.org/legacy/"
        echo "username = __token__"
        echo "password = your-testpypi-token"
        echo ""
        exit 1
    fi
    
    # Upload to TestPyPI
    twine upload --repository testpypi dist/*
    
    if [ $? -eq 0 ]; then
        print_success "Package published to TestPyPI successfully!"
        print_status "Package URL: https://test.pypi.org/project/cloudbulkupload/"
    else
        print_error "Failed to publish to TestPyPI"
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

# Main execution
main() {
    echo "🚀 TestPyPI Publishing Script for cloudbulkupload"
    echo "=================================================="
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
    display_package_info
    
    # Ask for confirmation before publishing
    echo ""
    read -p "Do you want to publish to TestPyPI? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        publish_to_testpypi
        echo ""
        print_success "TestPyPI publishing completed successfully!"
        print_status "You can now test the package installation:"
        echo "  pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ cloudbulkupload"
    else
        print_warning "Publishing cancelled by user"
        print_status "Package is built and ready for manual publishing"
    fi
}

# Run main function
main "$@"
