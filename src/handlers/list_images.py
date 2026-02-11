"""
Lambda handler for listing images with filters
"""
import json
from typing import Dict, Any
from src.utils.dynamodb_utils import list_images


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    List images with optional filters
    
    Supported query parameters:
    - user_id: Filter by user ID
    - tag: Filter by tag
    
    Example: GET /images?user_id=user123
    Example: GET /images?tag=sunset
    """
    try:
        # Extract query parameters
        query_params = event.get('queryStringParameters', {})
        
        if query_params is None:
            query_params = {}
        
        # Build filters
        filters = {}
        if 'user_id' in query_params:
            filters['user_id'] = query_params['user_id']
        elif 'tag' in query_params:
            filters['tag'] = query_params['tag']
        
        # Get images from DynamoDB
        images = list_images(filters if filters else None)
        
        # Remove sensitive data if needed
        for image in images:
            # Keep only necessary fields for listing
            pass
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'count': len(images),
                'images': images
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
