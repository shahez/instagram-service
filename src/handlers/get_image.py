"""
Lambda handler for viewing/downloading an image
"""
import json
import base64
from decimal import Decimal
from typing import Dict, Any
from src.utils.s3_utils import download_image, get_image_url
from src.utils.dynamodb_utils import get_image_metadata


def decimal_default(obj):
    """Helper to convert Decimal to int or float for JSON serialization"""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    View/download an image
    
    Path parameters:
    - image_id: The ID of the image to retrieve
    
    Query parameters:
    - download: Set to 'true' to get base64 encoded image data
    - url: Set to 'true' to get presigned URL instead
    
    Example: GET /images/{image_id}
    Example: GET /images/{image_id}?download=true
    Example: GET /images/{image_id}?url=true
    """
    try:
        # Extract image_id from path parameters
        path_params = event.get('pathParameters', {})
        
        if not path_params or 'image_id' not in path_params:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'image_id is required'})
            }
        
        image_id = path_params['image_id']
        query_params = event.get('queryStringParameters', {})
        
        if query_params is None:
            query_params = {}
        
        # Get metadata first
        metadata = get_image_metadata(image_id)
        
        if not metadata:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Image not found'})
            }
        
        # Check if user wants presigned URL
        if query_params.get('url', '').lower() == 'true':
            presigned_url = get_image_url(image_id)
            if not presigned_url:
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': 'Failed to generate presigned URL'})
                }
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'image_id': image_id,
                    'url': presigned_url,
                    'metadata': metadata
                }, default=decimal_default)
            }
        
        # Check if user wants to download
        if query_params.get('download', '').lower() == 'true':
            image_data = download_image(image_id)
            
            if not image_data:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': 'Image data not found'})
                }
            
            # Return base64 encoded image
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'image_id': image_id,
                    'image_data': base64.b64encode(image_data).decode('utf-8'),
                    'content_type': metadata.get('content_type', 'image/jpeg'),
                    'metadata': metadata
                }, default=decimal_default),
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
        
        # Default: return metadata only
        return {
            'statusCode': 200,
            'body': json.dumps({
                'image_id': image_id,
                'metadata': metadata
            }, default=decimal_default)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
