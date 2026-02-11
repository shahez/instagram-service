"""
Lambda handler for uploading images with metadata
"""
import json
import base64
import uuid
from datetime import datetime
from typing import Dict, Any
from src.utils.s3_utils import upload_image
from src.utils.dynamodb_utils import save_image_metadata


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Upload image with metadata
    
    Expected input:
    {
        "body": {
            "image": "base64_encoded_image",
            "user_id": "user123",
            "title": "My Image",
            "description": "Image description",
            "tags": ["sunset", "nature"]
        }
    }
    """
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Validate required fields
        if 'image' not in body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Image data is required'})
            }
        
        if 'user_id' not in body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'user_id is required'})
            }
        
        # Generate unique image ID
        image_id = str(uuid.uuid4())
        
        # Decode base64 image
        try:
            image_data = base64.b64decode(body['image'])
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Invalid base64 image data: {str(e)}'})
            }
        
        # Determine content type
        content_type = body.get('content_type', 'image/jpeg')
        
        # Upload image to S3
        if not upload_image(image_id, image_data, content_type):
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to upload image to S3'})
            }
        
        # Prepare metadata
        upload_date = datetime.utcnow().isoformat()
        metadata = {
            'image_id': image_id,
            'user_id': body['user_id'],
            'title': body.get('title', ''),
            'description': body.get('description', ''),
            'tags': body.get('tags', []),
            'upload_date': upload_date,
            'content_type': content_type,
            'size': len(image_data)
        }
        
        # Add tag for GSI if tags exist
        if metadata['tags']:
            metadata['tag'] = metadata['tags'][0]  # Use first tag for indexing
        
        # Save metadata to DynamoDB
        if not save_image_metadata(metadata):
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to save metadata'})
            }
        
        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'Image uploaded successfully',
                'image_id': image_id,
                'metadata': metadata
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
