"""
Unit tests for upload_image handler
"""
import json
import base64
import pytest
from unittest.mock import patch, MagicMock
from src.handlers.upload_image import lambda_handler


class TestUploadImage:
    """Test cases for upload image handler"""
    
    @patch('src.handlers.upload_image.upload_image')
    @patch('src.handlers.upload_image.save_image_metadata')
    def test_successful_upload(self, mock_save_metadata, mock_upload):
        """Test successful image upload"""
        # Mock successful operations
        mock_upload.return_value = True
        mock_save_metadata.return_value = True
        
        # Create test image data
        test_image = b"fake_image_data"
        encoded_image = base64.b64encode(test_image).decode('utf-8')
        
        event = {
            'body': json.dumps({
                'image': encoded_image,
                'user_id': 'user123',
                'title': 'Test Image',
                'description': 'Test description',
                'tags': ['test', 'demo']
            })
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert 'image_id' in body
        assert body['message'] == 'Image uploaded successfully'
        assert mock_upload.called
        assert mock_save_metadata.called
    
    def test_missing_image_data(self):
        """Test upload without image data"""
        event = {
            'body': json.dumps({
                'user_id': 'user123'
            })
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'Image data is required' in body['error']
    
    def test_missing_user_id(self):
        """Test upload without user_id"""
        test_image = b"fake_image_data"
        encoded_image = base64.b64encode(test_image).decode('utf-8')
        
        event = {
            'body': json.dumps({
                'image': encoded_image
            })
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'user_id is required' in body['error']
    
    def test_invalid_base64_image(self):
        """Test upload with invalid base64 data"""
        event = {
            'body': json.dumps({
                'image': 'invalid_base64_data!!!',
                'user_id': 'user123'
            })
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
    
    @patch('src.handlers.upload_image.upload_image')
    def test_s3_upload_failure(self, mock_upload):
        """Test S3 upload failure"""
        mock_upload.return_value = False
        
        test_image = b"fake_image_data"
        encoded_image = base64.b64encode(test_image).decode('utf-8')
        
        event = {
            'body': json.dumps({
                'image': encoded_image,
                'user_id': 'user123'
            })
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'Failed to upload image to S3' in body['error']
    
    @patch('src.handlers.upload_image.upload_image')
    @patch('src.handlers.upload_image.save_image_metadata')
    def test_metadata_save_failure(self, mock_save_metadata, mock_upload):
        """Test metadata save failure"""
        mock_upload.return_value = True
        mock_save_metadata.return_value = False
        
        test_image = b"fake_image_data"
        encoded_image = base64.b64encode(test_image).decode('utf-8')
        
        event = {
            'body': json.dumps({
                'image': encoded_image,
                'user_id': 'user123'
            })
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'Failed to save metadata' in body['error']
    
    @patch('src.handlers.upload_image.upload_image')
    @patch('src.handlers.upload_image.save_image_metadata')
    def test_upload_with_all_metadata(self, mock_save_metadata, mock_upload):
        """Test upload with complete metadata"""
        mock_upload.return_value = True
        mock_save_metadata.return_value = True
        
        test_image = b"fake_image_data"
        encoded_image = base64.b64encode(test_image).decode('utf-8')
        
        event = {
            'body': json.dumps({
                'image': encoded_image,
                'user_id': 'user123',
                'title': 'Sunset',
                'description': 'Beautiful sunset photo',
                'tags': ['sunset', 'nature', 'photography'],
                'content_type': 'image/png'
            })
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert body['metadata']['title'] == 'Sunset'
        assert body['metadata']['description'] == 'Beautiful sunset photo'
        assert len(body['metadata']['tags']) == 3
        assert body['metadata']['content_type'] == 'image/png'
