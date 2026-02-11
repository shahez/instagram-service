"""
Unit tests for list_images handler
"""
import json
import pytest
from unittest.mock import patch
from src.handlers.list_images import lambda_handler


class TestListImages:
    """Test cases for list images handler"""
    
    @patch('src.handlers.list_images.list_images')
    def test_list_all_images(self, mock_list):
        """Test listing all images without filters"""
        mock_list.return_value = [
            {
                'image_id': 'img1',
                'user_id': 'user123',
                'title': 'Image 1'
            },
            {
                'image_id': 'img2',
                'user_id': 'user456',
                'title': 'Image 2'
            }
        ]
        
        event = {
            'queryStringParameters': None
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['count'] == 2
        assert len(body['images']) == 2
        mock_list.assert_called_once_with(None)
    
    @patch('src.handlers.list_images.list_images')
    def test_filter_by_user_id(self, mock_list):
        """Test filtering images by user_id"""
        mock_list.return_value = [
            {
                'image_id': 'img1',
                'user_id': 'user123',
                'title': 'Image 1'
            }
        ]
        
        event = {
            'queryStringParameters': {
                'user_id': 'user123'
            }
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['count'] == 1
        mock_list.assert_called_once()
        call_args = mock_list.call_args[0][0]
        assert call_args['user_id'] == 'user123'
    
    @patch('src.handlers.list_images.list_images')
    def test_filter_by_tag(self, mock_list):
        """Test filtering images by tag"""
        mock_list.return_value = [
            {
                'image_id': 'img1',
                'tag': 'sunset',
                'title': 'Sunset Image'
            },
            {
                'image_id': 'img2',
                'tag': 'sunset',
                'title': 'Another Sunset'
            }
        ]
        
        event = {
            'queryStringParameters': {
                'tag': 'sunset'
            }
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['count'] == 2
        mock_list.assert_called_once()
        call_args = mock_list.call_args[0][0]
        assert call_args['tag'] == 'sunset'
    
    @patch('src.handlers.list_images.list_images')
    def test_empty_results(self, mock_list):
        """Test when no images are found"""
        mock_list.return_value = []
        
        event = {
            'queryStringParameters': {
                'user_id': 'nonexistent'
            }
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['count'] == 0
        assert body['images'] == []
    
    @patch('src.handlers.list_images.list_images')
    def test_database_error(self, mock_list):
        """Test handling of database errors"""
        mock_list.side_effect = Exception("Database error")
        
        event = {
            'queryStringParameters': None
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'error' in body
    
    @patch('src.handlers.list_images.list_images')
    def test_no_query_parameters(self, mock_list):
        """Test with missing queryStringParameters"""
        mock_list.return_value = []
        
        event = {}
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        mock_list.assert_called_once_with(None)
