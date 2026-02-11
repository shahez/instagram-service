"""
Local demo script that calls Lambda handlers directly (no API Gateway needed)
"""
import json
import base64
from PIL import Image
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.handlers.upload_image import lambda_handler as upload_handler
from src.handlers.list_images import lambda_handler as list_handler
from src.handlers.get_image import lambda_handler as get_handler
from src.handlers.delete_image import lambda_handler as delete_handler


def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_step(step_num, description):
    """Print a step description"""
    print(f"{step_num}. {description}")


def print_success(message):
    """Print success message"""
    print(f"✓ {message}")


def print_error(message):
    """Print error message"""
    print(f"✗ {message}")


def demo():
    """Demonstrate all Lambda handler operations"""
    print_header("Instagram Service Lambda Demo")
    
    # Create test image
    print_step(1, "Creating a test image...")
    try:
        test_image = Image.new('RGB', (200, 200), color='blue')
        test_image_path = 'test_demo_image.jpg'
        test_image.save(test_image_path)
        print_success(f"Test image created: {test_image_path}")
    except Exception as e:
        print_error(f"Failed to create image: {e}")
        return
    
    try:
        # Upload image
        print_step(2, "Uploading image...")
        with open(test_image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        upload_event = {
            'body': json.dumps({
                'image': image_data,
                'user_id': 'demo_user_123',
                'title': 'Demo Image',
                'description': 'This is a test image for the demo',
                'tags': ['demo', 'test', 'example'],
                'content_type': 'image/jpeg'
            })
        }
        
        upload_response = upload_handler(upload_event, None)
        
        if upload_response['statusCode'] == 201:
            upload_body = json.loads(upload_response['body'])
            image_id = upload_body['image_id']
            print_success("Image uploaded successfully")
            print(f"  Image ID: {image_id}")
            print(f"  Size: {upload_body['metadata']['size']} bytes")
        else:
            print_error(f"Upload failed: {upload_response['body']}")
            return
        
        # List all images
        print_step(3, "Listing all images...")
        list_event = {'queryStringParameters': None}
        list_response = list_handler(list_event, None)
        
        if list_response['statusCode'] == 200:
            list_body = json.loads(list_response['body'])
            print_success(f"Found {list_body['count']} image(s)")
        else:
            print_error(f"List failed: {list_response['body']}")
        
        # Filter by user
        print_step(4, "Filtering by user_id...")
        user_event = {'queryStringParameters': {'user_id': 'demo_user_123'}}
        user_response = list_handler(user_event, None)
        
        if user_response['statusCode'] == 200:
            user_body = json.loads(user_response['body'])
            print_success(f"Found {user_body['count']} image(s) for user 'demo_user_123'")
        else:
            print_error(f"Filter failed: {user_response['body']}")
        
        # Filter by tag
        print_step(5, "Filtering by tag 'demo'...")
        tag_event = {'queryStringParameters': {'tag': 'demo'}}
        tag_response = list_handler(tag_event, None)
        
        if tag_response['statusCode'] == 200:
            tag_body = json.loads(tag_response['body'])
            print_success(f"Found {tag_body['count']} image(s) with tag 'demo'")
        else:
            print_error(f"Filter failed: {tag_response['body']}")
        
        # Get metadata
        print_step(6, "Getting image metadata...")
        get_event = {
            'pathParameters': {'image_id': image_id},
            'queryStringParameters': None
        }
        get_response = get_handler(get_event, None)
        
        if get_response['statusCode'] == 200:
            get_body = json.loads(get_response['body'])
            metadata = get_body['metadata']
            print_success("Retrieved metadata")
            print(f"  Title: {metadata['title']}")
            print(f"  Upload date: {metadata['upload_date']}")
            print(f"  Tags: {', '.join(metadata['tags'])}")
        else:
            print_error(f"Get metadata failed: {get_response['body']}")
        
        # Get presigned URL
        print_step(7, "Getting presigned URL...")
        url_event = {
            'pathParameters': {'image_id': image_id},
            'queryStringParameters': {'url': 'true'}
        }
        url_response = get_handler(url_event, None)
        
        if url_response['statusCode'] == 200:
            url_body = json.loads(url_response['body'])
            print_success("Presigned URL generated")
            print(f"  URL: {url_body['url'][:80]}...")
        else:
            print_error(f"URL generation failed: {url_response['body']}")
        
        # Download image
        print_step(8, "Downloading image...")
        download_event = {
            'pathParameters': {'image_id': image_id},
            'queryStringParameters': {'download': 'true'}
        }
        download_response = get_handler(download_event, None)
        
        if download_response['statusCode'] == 200:
            download_body = json.loads(download_response['body'])
            image_bytes = base64.b64decode(download_body['image_data'])
            
            downloaded_path = 'downloaded_demo_image.jpg'
            with open(downloaded_path, 'wb') as f:
                f.write(image_bytes)
            print_success(f"Image downloaded and saved to {downloaded_path}")
            print(f"  Size: {len(image_bytes)} bytes")
        else:
            print_error(f"Download failed: {download_response['body']}")
        
        # Delete image
        print_step(9, "Deleting image...")
        delete_event = {'pathParameters': {'image_id': image_id}}
        delete_response = delete_handler(delete_event, None)
        
        if delete_response['statusCode'] == 200:
            delete_body = json.loads(delete_response['body'])
            print_success(delete_body['message'])
        else:
            print_error(f"Delete failed: {delete_response['body']}")
        
        # Verify deletion
        print_step(10, "Verifying deletion...")
        verify_event = {'queryStringParameters': {'user_id': 'demo_user_123'}}
        verify_response = list_handler(verify_event, None)
        
        if verify_response['statusCode'] == 200:
            verify_body = json.loads(verify_response['body'])
            remaining = sum(1 for img in verify_body['images'] if img['image_id'] == image_id)
            if remaining == 0:
                print_success("Image successfully deleted (not found in list)")
            else:
                print_error("Image still exists after deletion")
        
        print_header("Demo completed successfully!")
        print("\nAll Lambda handlers are working correctly.")
        print("The service is ready for deployment to AWS or API Gateway integration.\n")
        
    except Exception as e:
        print_error(f"Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        for path in ['test_demo_image.jpg', 'downloaded_demo_image.jpg']:
            if os.path.exists(path):
                os.remove(path)


if __name__ == '__main__':
    demo()
