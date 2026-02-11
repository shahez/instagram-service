"""
Integration tests for the Instagram service using moto
"""
import json
import base64
import pytest
import boto3
from moto import mock_s3, mock_dynamodb
from src.config import AWS_REGION, S3_BUCKET, DYNAMODB_TABLE
from src.handlers.upload_image import lambda_handler as upload_handler
from src.handlers.list_images import lambda_handler as list_handler
from src.handlers.get_image import lambda_handler as get_handler
from src.handlers.delete_image import lambda_handler as delete_handler


@pytest.fixture
def aws_credentials(monkeypatch):
    """Mock AWS credentials for moto"""
    monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'testing')
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'testing')
    monkeypatch.setenv('AWS_SECURITY_TOKEN', 'testing')
    monkeypatch.setenv('AWS_SESSION_TOKEN', 'testing')
    monkeypatch.setenv('USE_LOCALSTACK', 'false')


@pytest.fixture
def s3_setup(aws_credentials):
    """Set up mock S3"""
    with mock_s3():
        s3 = boto3.client('s3', region_name=AWS_REGION)
        s3.create_bucket(Bucket=S3_BUCKET)
        yield s3


@pytest.fixture
def dynamodb_setup(aws_credentials):
    """Set up mock DynamoDB"""
    with mock_dynamodb():
        dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)
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
        yield dynamodb


@pytest.fixture
def full_setup(s3_setup, dynamodb_setup):
    """Set up both S3 and DynamoDB"""
    yield


class TestIntegration:
    """Integration tests for the complete workflow"""
    
    def test_complete_workflow(self, full_setup):
        """Test complete upload -> list -> get -> delete workflow"""
        # 1. Upload an image
        test_image = b"fake_image_data_for_testing"
        encoded_image = base64.b64encode(test_image).decode('utf-8')
        
        upload_event = {
            'body': json.dumps({
                'image': encoded_image,
                'user_id': 'user123',
                'title': 'Integration Test Image',
                'description': 'Testing the complete workflow',
                'tags': ['test', 'integration']
            })
        }
        
        upload_response = upload_handler(upload_event, None)
        assert upload_response['statusCode'] == 201
        
        upload_body = json.loads(upload_response['body'])
        image_id = upload_body['image_id']
        
        # 2. List images
        list_event = {
            'queryStringParameters': None
        }
        list_response = list_handler(list_event, None)
        assert list_response['statusCode'] == 200
        
        list_body = json.loads(list_response['body'])
        assert list_body['count'] >= 1
        
        # 3. Get image metadata
        get_event = {
            'pathParameters': {'image_id': image_id},
            'queryStringParameters': None
        }
        get_response = get_handler(get_event, None)
        assert get_response['statusCode'] == 200
        
        get_body = json.loads(get_response['body'])
        assert get_body['image_id'] == image_id
        assert get_body['metadata']['title'] == 'Integration Test Image'
        
        # 4. Download image
        download_event = {
            'pathParameters': {'image_id': image_id},
            'queryStringParameters': {'download': 'true'}
        }
        download_response = get_handler(download_event, None)
        assert download_response['statusCode'] == 200
        
        download_body = json.loads(download_response['body'])
        downloaded_data = base64.b64decode(download_body['image_data'])
        assert downloaded_data == test_image
        
        # 5. Delete image
        delete_event = {
            'pathParameters': {'image_id': image_id}
        }
        delete_response = delete_handler(delete_event, None)
        assert delete_response['statusCode'] == 200
        
        # 6. Verify deletion
        verify_event = {
            'pathParameters': {'image_id': image_id},
            'queryStringParameters': None
        }
        verify_response = get_handler(verify_event, None)
        assert verify_response['statusCode'] == 404
    
    def test_filter_by_user_id(self, full_setup):
        """Test filtering images by user_id"""
        # Upload images for different users
        for i in range(3):
            test_image = f"image_{i}".encode()
            encoded_image = base64.b64encode(test_image).decode('utf-8')
            
            event = {
                'body': json.dumps({
                    'image': encoded_image,
                    'user_id': f'user{i % 2}',  # user0 and user1
                    'title': f'Image {i}'
                })
            }
            upload_handler(event, None)
        
        # Filter by user0
        list_event = {
            'queryStringParameters': {'user_id': 'user0'}
        }
        response = list_handler(list_event, None)
        body = json.loads(response['body'])
        
        # Should get 2 images (i=0 and i=2)
        assert body['count'] == 2
        for image in body['images']:
            assert image['user_id'] == 'user0'
    
    def test_filter_by_tag(self, full_setup):
        """Test filtering images by tag"""
        # Upload images with different tags
        tags_list = [['nature', 'sunset'], ['city', 'night'], ['nature', 'forest']]
        
        for i, tags in enumerate(tags_list):
            test_image = f"image_{i}".encode()
            encoded_image = base64.b64encode(test_image).decode('utf-8')
            
            event = {
                'body': json.dumps({
                    'image': encoded_image,
                    'user_id': 'user123',
                    'title': f'Image {i}',
                    'tags': tags
                })
            }
            upload_handler(event, None)
        
        # Filter by 'nature' tag
        list_event = {
            'queryStringParameters': {'tag': 'nature'}
        }
        response = list_handler(list_event, None)
        body = json.loads(response['body'])
        
        # Should get 2 images with 'nature' tag
        assert body['count'] == 2
