"""
Setup script to initialize LocalStack resources
"""
import boto3
import sys
from src.utils.dynamodb_utils import create_table
from src.utils.s3_utils import create_bucket


def main():
    """Initialize LocalStack resources"""
    print("Initializing LocalStack resources...")
    
    try:
        # Create S3 bucket
        print("Creating S3 bucket...")
        create_bucket()
        
        # Create DynamoDB table
        print("Creating DynamoDB table...")
        create_table()
        
        print("\n✓ LocalStack resources initialized successfully!")
        return 0
    
    except Exception as e:
        print(f"\n✗ Error initializing resources: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
