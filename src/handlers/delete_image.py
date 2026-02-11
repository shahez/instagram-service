"""
Lambda handler for deleting an image
"""
import json
from typing import Dict, Any
from src.utils.s3_utils import delete_image as s3_delete_image
from src.utils.dynamodb_utils import delete_image_metadata, get_image_metadata


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Delete an image and its metadata
    
    Path parameters:
    - image_id: The ID of the image to delete
    
    Example: DELETE /images/{image_id}
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
        
        # Check if image exists
        metadata = get_image_metadata(image_id)
        
        if not metadata:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Image not found'})
            }
        
        # Delete from S3
        s3_deleted = s3_delete_image(image_id)
        
        # Delete metadata from DynamoDB
        db_deleted = delete_image_metadata(image_id)
        
        if not s3_deleted or not db_deleted:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Failed to delete image completely',
                    's3_deleted': s3_deleted,
                    'metadata_deleted': db_deleted
                })
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Image deleted successfully',
                'image_id': image_id
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
