"""
DynamoDB utility module for image metadata operations
"""
import boto3
from datetime import datetime
from typing import Dict, List, Optional
from src.config import (
    AWS_REGION, DYNAMODB_TABLE, LOCALSTACK_ENDPOINT,
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, USE_LOCALSTACK
)


def get_dynamodb_client():
    """Initialize and return DynamoDB client"""
    if USE_LOCALSTACK:
        return boto3.client(
            'dynamodb',
            endpoint_url=LOCALSTACK_ENDPOINT,
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    return boto3.client('dynamodb', region_name=AWS_REGION)


def get_dynamodb_resource():
    """Initialize and return DynamoDB resource"""
    if USE_LOCALSTACK:
        return boto3.resource(
            'dynamodb',
            endpoint_url=LOCALSTACK_ENDPOINT,
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    return boto3.resource('dynamodb', region_name=AWS_REGION)


def create_table():
    """Create DynamoDB table if it doesn't exist"""
    dynamodb = get_dynamodb_client()
    
    try:
        dynamodb.describe_table(TableName=DYNAMODB_TABLE)
        print(f"Table {DYNAMODB_TABLE} already exists")
    except dynamodb.exceptions.ResourceNotFoundException:
        dynamodb.create_table(
            TableName=DYNAMODB_TABLE,
            KeySchema=[
                {'AttributeName': 'image_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'image_id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'upload_date', 'AttributeType': 'S'},
                {'AttributeName': 'tag', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'user_id-index',
                    'KeySchema': [
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'upload_date', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                },
                {
                    'IndexName': 'tag-index',
                    'KeySchema': [
                        {'AttributeName': 'tag', 'KeyType': 'HASH'},
                        {'AttributeName': 'upload_date', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print(f"Table {DYNAMODB_TABLE} created successfully")


def save_image_metadata(metadata: Dict) -> bool:
    """Save image metadata to DynamoDB"""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(DYNAMODB_TABLE)
        
        table.put_item(Item=metadata)
        return True
    except Exception as e:
        print(f"Error saving metadata: {str(e)}")
        return False


def get_image_metadata(image_id: str) -> Optional[Dict]:
    """Retrieve image metadata by image_id"""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(DYNAMODB_TABLE)
        
        response = table.get_item(Key={'image_id': image_id})
        return response.get('Item')
    except Exception as e:
        print(f"Error retrieving metadata: {str(e)}")
        return None


def delete_image_metadata(image_id: str) -> bool:
    """Delete image metadata from DynamoDB"""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(DYNAMODB_TABLE)
        
        table.delete_item(Key={'image_id': image_id})
        return True
    except Exception as e:
        print(f"Error deleting metadata: {str(e)}")
        return False


def list_images(filters: Optional[Dict] = None) -> List[Dict]:
    """
    List images with optional filters
    Supported filters: user_id, tag
    """
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(DYNAMODB_TABLE)
        
        if filters:
            if 'user_id' in filters:
                response = table.query(
                    IndexName='user_id-index',
                    KeyConditionExpression='user_id = :uid',
                    ExpressionAttributeValues={':uid': filters['user_id']},
                    ScanIndexForward=False
                )
            elif 'tag' in filters:
                response = table.query(
                    IndexName='tag-index',
                    KeyConditionExpression='tag = :tag',
                    ExpressionAttributeValues={':tag': filters['tag']},
                    ScanIndexForward=False
                )
            else:
                response = table.scan()
        else:
            response = table.scan()
        
        return response.get('Items', [])
    except Exception as e:
        print(f"Error listing images: {str(e)}")
        return []
