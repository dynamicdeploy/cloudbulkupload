#!/usr/bin/env python3
"""
Hybrid Approach Demo: Standard Mode vs Transfer Manager Mode

This script demonstrates how to use both upload modes in cloudbulkupload:
1. Standard Mode - Consistent API across all cloud providers
2. Transfer Manager Mode - High-performance Google Cloud specific mode
"""

import asyncio
import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_demo_files():
    """Create demo files for testing"""
    files = []
    temp_dir = tempfile.mkdtemp()
    
    # Create small files for standard mode
    for i in range(3):
        filename = f"small_file_{i}.txt"
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write(f"Small file {i} content" + "A" * 1024)  # ~1KB
        files.append(filepath)
    
    # Create larger files for transfer manager mode
    for i in range(2):
        filename = f"large_file_{i}.txt"
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write("Large file content" + "A" * 1024 * 1024)  # ~1MB
        files.append(filepath)
    
    return files, temp_dir

async def demo_hybrid_approach():
    """Demonstrate the hybrid approach"""
    print("🚀 Hybrid Approach Demo: Standard vs Transfer Manager")
    print("=" * 60)
    
    # Check if Google Cloud credentials are available
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    credentials_path = os.getenv("GOOGLE_CLOUD_CREDENTIALS_PATH")
    
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT_ID not found in environment")
        print("Please set up your Google Cloud credentials in .env file")
        return
    
    try:
        from cloudbulkupload import BulkGoogleStorage, StorageTransferPath
        
        # Initialize client
        client = BulkGoogleStorage(
            project_id=project_id,
            credentials_path=credentials_path,
            max_concurrent_operations=50,
            verbose=True
        )
        
        # Create demo files
        files, temp_dir = create_demo_files()
        
        print(f"📁 Created {len(files)} demo files in {temp_dir}")
        
        # Prepare upload paths
        upload_paths = []
        for file_path in files:
            filename = os.path.basename(file_path)
            upload_paths.append(StorageTransferPath(
                local_path=file_path,
                storage_path=f"demo/{filename}"
            ))
        
        # Demo bucket name
        bucket_name = "cloudbulkupload-demo"
        
        print(f"\n🔧 Using bucket: {bucket_name}")
        print("Note: This is a demonstration. In a real environment, you would:")
        print("1. Create the bucket if it doesn't exist")
        print("2. Upload files using both modes")
        print("3. Compare performance")
        print("4. Clean up resources")
        
        print(f"\n📋 Upload Paths:")
        for path in upload_paths:
            print(f"  {path.local_path} → {path.storage_path}")
        
        print(f"\n🎯 Usage Examples:")
        print(f"1. Standard Mode (Consistent API):")
        print(f"   await client.upload_files('{bucket_name}', upload_paths)")
        print(f"   # Use this for multi-cloud applications")
        
        print(f"\n2. Transfer Manager Mode (High Performance):")
        print(f"   await client.upload_files('{bucket_name}', upload_paths, use_transfer_manager=True)")
        print(f"   # Use this for Google Cloud only, max performance")
        
        print(f"\n3. Smart Mode Selection:")
        print(f"   # Choose mode based on requirements")
        print(f"   use_tm = is_google_only and needs_max_performance")
        print(f"   await client.upload_files('{bucket_name}', upload_paths, use_transfer_manager=use_tm)")
        
        print(f"\n📊 Performance Comparison:")
        print(f"| Mode | Speed | Use Case |")
        print(f"|------|-------|----------|")
        print(f"| Standard | ~5.94 MB/s | Multi-cloud, consistent API |")
        print(f"| Transfer Manager | ~8.87 MB/s | Google Cloud, max performance |")
        
        print(f"\n🎉 Benefits of Hybrid Approach:")
        print(f"✅ Same API for both modes")
        print(f"✅ Automatic fallback if Transfer Manager fails")
        print(f"✅ Performance optimization when needed")
        print(f"✅ Consistent error handling")
        print(f"✅ Easy migration between modes")
        
        # Clean up demo files
        for file_path in files:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.rmdir(temp_dir)
        
        print(f"\n💡 Best Practices:")
        print(f"1. Use Standard Mode for:")
        print(f"   - Multi-cloud applications")
        print(f"   - Small files (< 100MB)")
        print(f"   - When API consistency matters")
        
        print(f"\n2. Use Transfer Manager Mode for:")
        print(f"   - Google Cloud only applications")
        print(f"   - Large files (> 100MB)")
        print(f"   - Bulk uploads (> 100 files)")
        print(f"   - When maximum performance is critical")
        
        print(f"\n3. Smart Selection:")
        print(f"   - Monitor performance")
        print(f"   - Test both modes")
        print(f"   - Choose based on your specific use case")
        
    except ImportError:
        print("❌ cloudbulkupload not installed")
        print("Install with: pip install cloudbulkupload[google-cloud]")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("This is expected if Google Cloud credentials are not properly configured")

if __name__ == "__main__":
    asyncio.run(demo_hybrid_approach())
