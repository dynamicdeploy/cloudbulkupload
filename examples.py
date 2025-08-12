import logging
import os
from pathlib import Path

# Import python-dotenv to load environment variables from .env file
from dotenv import load_dotenv

from cloudbulkupload import BulkBoto3, StorageTransferPath

# Load environment variables from .env file
# This will automatically load AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_ENDPOINT_URL
load_dotenv()

# Configure logging for the examples
logging.basicConfig(
    level="INFO",
    format="%(asctime)s — %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Configuration constants
TARGET_BUCKET = "test-bucket"
NUM_TRANSFER_THREADS = 50
TRANSFER_VERBOSITY = True

# Read AWS credentials and endpoint from environment variables
# These are loaded from the .env file using load_dotenv()
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localhost:9000")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Validate that required environment variables are present
if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    raise ValueError(
        "AWS credentials not found in environment variables. "
        "Please ensure your .env file contains AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
    )

print(f"Using endpoint: {AWS_ENDPOINT_URL}")
print(f"Access key: {AWS_ACCESS_KEY_ID[:8]}...")  # Show first 8 characters for verification

# Instantiate a BulkBoto3 object with credentials from .env file
bulkboto_agent = BulkBoto3(
    resource_type="s3",
    endpoint_url=AWS_ENDPOINT_URL,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    max_pool_connections=300,
    verbose=TRANSFER_VERBOSITY,
)

print("✅ BulkBoto3 agent initialized successfully with .env credentials")

# Create a new bucket for testing
print(f"\n📦 Creating bucket: {TARGET_BUCKET}")
bulkboto_agent.create_new_bucket(bucket_name=TARGET_BUCKET)

# Create test directory structure if it doesn't exist
test_dir = Path("test_dir")
test_dir.mkdir(exist_ok=True)
(test_dir / "first_subdir").mkdir(exist_ok=True)
(test_dir / "second_subdir").mkdir(exist_ok=True)

# Create some test files
(test_dir / "first_subdir" / "f2").write_text("This is test file f2")
(test_dir / "second_subdir" / "f4").write_text("This is test file f4")
(test_dir / "first_subdir" / "test_file.txt").write_text("This is a test file")
(test_dir / "first_subdir" / "f1").write_text("This is test file f1")

print(f"✅ Created test directory structure in {test_dir}")

# Upload a whole directory with its structure to an S3 bucket in multi-thread mode
print(f"\n📤 Uploading directory to S3 with {NUM_TRANSFER_THREADS} threads...")
bulkboto_agent.upload_dir_to_storage(
    bucket_name=TARGET_BUCKET,
    local_dir="test_dir",
    storage_dir="my_storage_dir",
    n_threads=NUM_TRANSFER_THREADS,
)
print("✅ Directory upload completed")

# Download a whole directory with its structure to a local directory in multi-thread mode
print(f"\n📥 Downloading directory from S3 with {NUM_TRANSFER_THREADS} threads...")
bulkboto_agent.download_dir_from_storage(
    bucket_name=TARGET_BUCKET,
    storage_dir="my_storage_dir",
    local_dir="new_test_dir",
    n_threads=NUM_TRANSFER_THREADS,
)
print("✅ Directory download completed")

# Upload arbitrary files to an S3 bucket
print("\n📤 Uploading specific files to S3...")
upload_paths = [
    StorageTransferPath(
        local_path="test_dir/first_subdir/f2",
        storage_path="f2",
    ),
    StorageTransferPath(
        local_path="test_dir/second_subdir/f4",
        storage_path="my_storage_dir/f4",
    ),
]
bulkboto_agent.upload(bucket_name=TARGET_BUCKET, upload_paths=upload_paths)
print("✅ Specific files upload completed")

# Download arbitrary files from an S3 bucket
print("\n📥 Downloading specific files from S3...")
download_paths = [
    StorageTransferPath(
        storage_path="f2",
        local_path="f2",
    ),
    StorageTransferPath(
        storage_path="my_storage_dir/f4",
        local_path="f5",
    ),
]
bulkboto_agent.download(
    bucket_name=TARGET_BUCKET, download_paths=download_paths
)
print("✅ Specific files download completed")

# Check if files exist in the bucket
print("\n🔍 Checking if files exist in the bucket...")
exists1 = bulkboto_agent.check_object_exists(
    bucket_name=TARGET_BUCKET,
    object_path="my_storage_dir/first_subdir/test_file.txt",
)
exists2 = bulkboto_agent.check_object_exists(
    bucket_name=TARGET_BUCKET, object_path="my_storage_dir/first_subdir/f1"
)
print(f"File 'my_storage_dir/first_subdir/test_file.txt' exists: {exists1}")
print(f"File 'my_storage_dir/first_subdir/f1' exists: {exists2}")

# Get list of objects in a bucket (with prefix)
print("\n📋 Listing objects in the bucket...")
objects1 = bulkboto_agent.list_objects(
    bucket_name=TARGET_BUCKET, storage_dir="my_storage_dir"
)
objects2 = bulkboto_agent.list_objects(
    bucket_name=TARGET_BUCKET, storage_dir="my_storage_dir/second_subdir"
)
print(f"Objects in 'my_storage_dir': {len(objects1)} files")
print(f"Objects in 'my_storage_dir/second_subdir': {len(objects2)} files")

# Delete all objects on the bucket (cleanup)
print(f"\n🧹 Cleaning up bucket: {TARGET_BUCKET}")
bulkboto_agent.empty_bucket(TARGET_BUCKET)
print("✅ Bucket cleanup completed")

print("\n🎉 All examples completed successfully!")
print("📝 Check the created files and directories to verify the operations worked correctly.")
