import tempfile
import shutil
import os

def create_temp_directory():
    """
    Creates and returns a temporary directory path.
    This directory will be used to store files downloaded from the source storage.
    """
    temp_dir = tempfile.mkdtemp()
    print(f"🌐 Created temporary directory: {temp_dir}")
    return temp_dir

def cleanup_temp_directory(temp_dir):
    """
    Cleans up (removes) the temporary directory and its contents after the migration.
    """
    print(f"🧹 Cleaning up temporary directory: {temp_dir}")
    shutil.rmtree(temp_dir)
    print(f"✅ Temporary directory {temp_dir} removed successfully!")
