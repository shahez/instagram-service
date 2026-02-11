"""
Unit tests for delete_image handler
"""
import json
import pytest
from unittest.mock import patch
from src.handlers.delete_image import lambda_handler


class TestDeleteImage:
    """Test cases for delete image handler"""
    
    @patch('src.handlers.delete_image.get_image_metadata')
    @patch('src.handlers.delete_image.s3_delete_image')
    @patch('src.handlers.delete_image.delete_image_metadata')
    def test_successful_delete(self, mock_delete_metadata, mock_delete_s3, mock_get_metadata):
        """Test successful image deletion"""
        mock_get_metadata.return_value = {
            'image_id': 'img123',
            'user_id': 'user123'
        }
        mock_delete_s3.return_value = True
        mock_delete_metadata.return_value = True
        
        event = {
            'pathParameters': {
                'image_id': 'img123'
            }
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['message'] == 'Image deleted successfully'
        assert body['image_id'] == 'img123'
        assert mock_delete_s3.called
        assert mock_delete_metadata.called
    
    def test_missing_image_id(self):
        """Test delete request without image_id"""
        event = {
            'pathParameters': {}
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'image_id is required' in body['error']
    
    @patch('src.handlers.delete_image.get_image_metadata')
    def test_delete_nonexistent_image(self, mock_get_metadata):
        """Test deleting an image that doesn't exist"""
        mock_get_metadata.return_value = None
        
        event = {
            'pathParameters': {
                'image_id': 'nonexistent'
            }
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'Image not found' in body['error']
    
    @patch('src.handlers.delete_image.get_image_metadata')
    @patch('src.handlers.delete_image.s3_delete_image')
    @patch('src.handlers.delete_image.delete_image_metadata')
    def test_s3_delete_failure(self, mock_delete_metadata, mock_delete_s3, mock_get_metadata):
        """Test when S3 deletion fails"""
        mock_get_metadata.return_value = {'image_id': 'img123'}
        mock_delete_s3.return_value = False
        mock_delete_metadata.return_value = True
        
        event = {
            'pathParameters': {
                'image_id': 'img123'
            }
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'Failed to delete image completely' in body['error']
    
    @patch('src.handlers.delete_image.get_image_metadata')
    @patch('src.handlers.delete_image.s3_delete_image')
    @patch('src.handlers.delete_image.delete_image_metadata')
    def test_metadata_delete_failure(self, mock_delete_metadata, mock_delete_s3, mock_get_metadata):
        """Test when metadata deletion fails"""
        mock_get_metadata.return_value = {'image_id': 'img123'}
        mock_delete_s3.return_value = True
        mock_delete_metadata.return_value = False
        
        event = {
            'pathParameters': {
                'image_id': 'img123'
            }
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'Failed to delete image completely' in body['error']
    
    @patch('src.handlers.delete_image.get_image_metadata')
    @patch('src.handlers.delete_image.s3_delete_image')
    @patch('src.handlers.delete_image.delete_image_metadata')
    def test_both_deletes_fail(self, mock_delete_metadata, mock_delete_s3, mock_get_metadata):
        """Test when both S3 and metadata deletion fail"""
        mock_get_metadata.return_value = {'image_id': 'img123'}
        mock_delete_s3.return_value = False
        mock_delete_metadata.return_value = False
        
        event = {
            'pathParameters': {
                'image_id': 'img123'
            }
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'Failed to delete image completely' in body['error']
        assert body['s3_deleted'] == False
        assert body['metadata_deleted'] == False
    
    @patch('src.handlers.delete_image.get_image_metadata')
    def test_exception_handling(self, mock_get_metadata):
        """Test exception handling during deletion"""
        mock_get_metadata.side_effect = Exception("Database error")
        
        event = {
            'pathParameters': {
                'image_id': 'img123'
            }
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'Internal server error' in body['error']
