"""
S3 utility module for image storage operations
"""
import boto3
import base64
from typing import Optional
from src.config import (
    AWS_REGION, S3_BUCKET, LOCALSTACK_ENDPOINT,
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, USE_LOCALSTACK
)


def get_s3_client():
    """Initialize and return S3 client"""
    if USE_LOCALSTACK:
        return boto3.client(
            's3',
            endpoint_url=LOCALSTACK_ENDPOINT,
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    return boto3.client('s3', region_name=AWS_REGION)


def create_bucket():
    """Create S3 bucket if it doesn't exist"""
    s3 = get_s3_client()
    
    try:
        s3.head_bucket(Bucket=S3_BUCKET)
        print(f"Bucket {S3_BUCKET} already exists")
    except:
        try:
            if AWS_REGION == 'us-east-1':
                s3.create_bucket(Bucket=S3_BUCKET)
            else:
                s3.create_bucket(
                    Bucket=S3_BUCKET,
                    CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
                )
            print(f"Bucket {S3_BUCKET} created successfully")
        except Exception as e:
            print(f"Error creating bucket: {str(e)}")


def upload_image(image_id: str, image_data: bytes, content_type: str = 'image/jpeg') -> bool:
    """Upload image to S3"""
    try:
        s3 = get_s3_client()
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=image_id,
            Body=image_data,
            ContentType=content_type
        )
        return True
    except Exception as e:
        print(f"Error uploading image: {str(e)}")
        return False


def download_image(image_id: str) -> Optional[bytes]:
    """Download image from S3"""
    try:
        s3 = get_s3_client()
        response = s3.get_object(Bucket=S3_BUCKET, Key=image_id)
        return response['Body'].read()
    except Exception as e:
        print(f"Error downloading image: {str(e)}")
        return None


def delete_image(image_id: str) -> bool:
    """Delete image from S3"""
    try:
        s3 = get_s3_client()
        s3.delete_object(Bucket=S3_BUCKET, Key=image_id)
        return True
    except Exception as e:
        print(f"Error deleting image: {str(e)}")
        return False


def get_image_url(image_id: str, expiration: int = 3600) -> Optional[str]:
    """Generate presigned URL for image"""
    try:
        s3 = get_s3_client()
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': image_id},
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        print(f"Error generating URL: {str(e)}")
        return None
