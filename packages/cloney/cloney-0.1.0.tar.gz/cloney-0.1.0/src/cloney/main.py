import sys
import argparse
from cloney.storage import download_from_source, upload_to_destination
from cloney.utils import create_temp_directory, cleanup_temp_directory

def main():
    parser = argparse.ArgumentParser(description="Cloney - Cloud Storage Migration Tool")
    parser.add_argument("source_service", help="Source storage service (s3, gcs, oss, azure)")
    parser.add_argument("source_bucket", help="Source bucket name")
    parser.add_argument("destination_service", help="Destination storage service (s3, gcs, oss, azure)")
    parser.add_argument("destination_bucket", help="Destination bucket name")
    

    args = parser.parse_args()

    temp_dir = create_temp_directory()

    try:

        print(f"Downloading files from {args.source_service}://{args.source_bucket} to local directory...")
        download_from_source(args.source_service, args.source_bucket, temp_dir)

        print(f"Uploading files from local directory to {args.destination_service}://{args.destination_bucket}...")
        upload_to_destination(args.destination_service, args.destination_bucket, temp_dir)

        print(f"Migration from {args.source_service}://{args.source_bucket} to {args.destination_service}://{args.destination_bucket} completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    finally:
        print(f"Cleaning up temporary directory: {temp_dir}")
        cleanup_temp_directory(temp_dir)

if __name__ == "__main__":
    main()
