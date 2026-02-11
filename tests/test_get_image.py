"""
Unit tests for get_image handler
"""
import json
import base64
import pytest
from unittest.mock import patch
from src.handlers.get_image import lambda_handler


class TestGetImage:
    """Test cases for get image handler"""
    
    @patch('src.handlers.get_image.get_image_metadata')
    def test_get_metadata_only(self, mock_get_metadata):
        """Test getting image metadata only"""
        mock_get_metadata.return_value = {
            'image_id': 'img123',
            'user_id': 'user123',
            'title': 'Test Image',
            'upload_date': '2026-02-11T10:00:00'
        }
        
        event = {
            'pathParameters': {
                'image_id': 'img123'
            },
            'queryStringParameters': None
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['image_id'] == 'img123'
        assert 'metadata' in body
        assert body['metadata']['title'] == 'Test Image'
    
    def test_missing_image_id(self):
        """Test request without image_id"""
        event = {
            'pathParameters': {}
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'image_id is required' in body['error']
    
    @patch('src.handlers.get_image.get_image_metadata')
    def test_image_not_found(self, mock_get_metadata):
        """Test when image doesn't exist"""
        mock_get_metadata.return_value = None
        
        event = {
            'pathParameters': {
                'image_id': 'nonexistent'
            },
            'queryStringParameters': None
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'Image not found' in body['error']
    
    @patch('src.handlers.get_image.get_image_metadata')
    @patch('src.handlers.get_image.get_image_url')
    def test_get_presigned_url(self, mock_get_url, mock_get_metadata):
        """Test getting presigned URL"""
        mock_get_metadata.return_value = {
            'image_id': 'img123',
            'user_id': 'user123'
        }
        mock_get_url.return_value = 'https://s3.amazonaws.com/presigned-url'
        
        event = {
            'pathParameters': {
                'image_id': 'img123'
            },
            'queryStringParameters': {
                'url': 'true'
            }
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'url' in body
        assert body['url'] == 'https://s3.amazonaws.com/presigned-url'
    
    @patch('src.handlers.get_image.get_image_metadata')
    @patch('src.handlers.get_image.download_image')
    def test_download_image(self, mock_download, mock_get_metadata):
        """Test downloading image data"""
        mock_get_metadata.return_value = {
            'image_id': 'img123',
            'content_type': 'image/jpeg'
        }
        test_image = b"fake_image_data"
        mock_download.return_value = test_image
        
        event = {
            'pathParameters': {
                'image_id': 'img123'
            },
            'queryStringParameters': {
                'download': 'true'
            }
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'image_data' in body
        decoded_data = base64.b64decode(body['image_data'])
        assert decoded_data == test_image
    
    @patch('src.handlers.get_image.get_image_metadata')
    @patch('src.handlers.get_image.download_image')
    def test_download_image_not_found(self, mock_download, mock_get_metadata):
        """Test when image file doesn't exist in S3"""
        mock_get_metadata.return_value = {
            'image_id': 'img123'
        }
        mock_download.return_value = None
        
        event = {
            'pathParameters': {
                'image_id': 'img123'
            },
            'queryStringParameters': {
                'download': 'true'
            }
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'Image data not found' in body['error']
    
    @patch('src.handlers.get_image.get_image_metadata')
    @patch('src.handlers.get_image.get_image_url')
    def test_presigned_url_generation_fails(self, mock_get_url, mock_get_metadata):
        """Test when presigned URL generation fails"""
        mock_get_metadata.return_value = {
            'image_id': 'img123'
        }
        mock_get_url.return_value = None
        
        event = {
            'pathParameters': {
                'image_id': 'img123'
            },
            'queryStringParameters': {
                'url': 'true'
            }
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'Failed to generate presigned URL' in body['error']
