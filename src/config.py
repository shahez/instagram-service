"""
Configuration module for Instagram Service
"""
import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
DYNAMODB_TABLE = os.getenv('DYNAMODB_TABLE', 'instagram-images')
S3_BUCKET = os.getenv('S3_BUCKET', 'instagram-images-bucket')
LOCALSTACK_ENDPOINT = os.getenv('LOCALSTACK_ENDPOINT', 'http://localhost:4566')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'test')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'test')

# Use LocalStack endpoint if in development
USE_LOCALSTACK = os.getenv('USE_LOCALSTACK', 'true').lower() == 'true'
