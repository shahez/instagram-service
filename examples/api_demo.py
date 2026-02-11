"""
Example script demonstrating API usage
"""
import json
import base64
import requests
import time
from pathlib import Path


class InstagramServiceClient:
    """Simple client for Instagram Service API"""
    
    def __init__(self, base_url="http://localhost:4566"):
        self.base_url = base_url
    
    def upload_image(self, image_path, user_id, title="", description="", tags=None):
        """Upload an image"""
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Determine content type
        ext = Path(image_path).suffix.lower()
        content_type = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif'
        }.get(ext, 'image/jpeg')
        
        payload = {
            'image': image_data,
            'user_id': user_id,
            'title': title,
            'description': description,
            'tags': tags or [],
            'content_type': content_type
        }
        
        response = requests.post(f"{self.base_url}/images", json=payload)
        return response.json()
    
    def list_images(self, user_id=None, tag=None):
        """List images with optional filters"""
        params = {}
        if user_id:
            params['user_id'] = user_id
        elif tag:
            params['tag'] = tag
        
        response = requests.get(f"{self.base_url}/images", params=params)
        return response.json()
    
    def get_image(self, image_id, download=False, get_url=False):
        """Get image metadata or download image"""
        params = {}
        if download:
            params['download'] = 'true'
        elif get_url:
            params['url'] = 'true'
        
        response = requests.get(f"{self.base_url}/images/{image_id}", params=params)
        return response.json()
    
    def delete_image(self, image_id):
        """Delete an image"""
        response = requests.delete(f"{self.base_url}/images/{image_id}")
        return response.json()
    
    def download_and_save(self, image_id, output_path):
        """Download image and save to file"""
        result = self.get_image(image_id, download=True)
        
        if 'image_data' in result:
            image_bytes = base64.b64decode(result['image_data'])
            with open(output_path, 'wb') as f:
                f.write(image_bytes)
            print(f"Image saved to {output_path}")
            return True
        return False


def demo():
    """Demonstrate all API operations"""
    client = InstagramServiceClient()
    
    print("=" * 60)
    print("Instagram Service API Demo")
    print("=" * 60)
    
    # Note: You'll need to create a test image or update the path
    print("\n1. Creating a test image...")
    # Create a simple test image
    from PIL import Image
    test_image = Image.new('RGB', (100, 100), color='red')
    test_image.save('test_image.jpg')
    print("✓ Test image created: test_image.jpg")
    
    # 1. Upload image
    print("\n2. Uploading image...")
    try:
        upload_result = client.upload_image(
            'test_image.jpg',
            user_id='demo_user',
            title='Demo Image',
            description='This is a test image for the demo',
            tags=['demo', 'test', 'example']
        )
        print("✓ Image uploaded successfully")
        print(f"  Image ID: {upload_result['image_id']}")
        image_id = upload_result['image_id']
    except Exception as e:
        print(f"✗ Upload failed: {str(e)}")
        print("\nMake sure LocalStack is running:")
        print("  docker-compose up -d")
        print("  make setup")
        return
    
    # 2. List all images
    print("\n3. Listing all images...")
    list_result = client.list_images()
    print(f"✓ Found {list_result['count']} image(s)")
    
    # 3. Filter by user
    print("\n4. Filtering by user_id...")
    user_images = client.list_images(user_id='demo_user')
    print(f"✓ Found {user_images['count']} image(s) for user 'demo_user'")
    
    # 4. Filter by tag
    print("\n5. Filtering by tag 'demo'...")
    tagged_images = client.list_images(tag='demo')
    print(f"✓ Found {tagged_images['count']} image(s) with tag 'demo'")
    
    # 5. Get metadata
    print("\n6. Getting image metadata...")
    metadata = client.get_image(image_id)
    print(f"✓ Retrieved metadata for image: {metadata['metadata']['title']}")
    print(f"  Upload date: {metadata['metadata']['upload_date']}")
    print(f"  Tags: {', '.join(metadata['metadata']['tags'])}")
    
    # 6. Get presigned URL
    print("\n7. Getting presigned URL...")
    url_result = client.get_image(image_id, get_url=True)
    print(f"✓ Presigned URL: {url_result['url'][:60]}...")
    
    # 7. Download image
    print("\n8. Downloading image...")
    client.download_and_save(image_id, 'downloaded_image.jpg')
    print("✓ Image downloaded and saved")
    
    # 8. Delete image
    print("\n9. Deleting image...")
    delete_result = client.delete_image(image_id)
    print(f"✓ {delete_result['message']}")
    
    # 9. Verify deletion
    print("\n10. Verifying deletion...")
    list_result = client.list_images(user_id='demo_user')
    print(f"✓ User now has {list_result['count']} image(s)")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
    
    # Cleanup
    import os
    if os.path.exists('test_image.jpg'):
        os.remove('test_image.jpg')
    if os.path.exists('downloaded_image.jpg'):
        os.remove('downloaded_image.jpg')


if __name__ == '__main__':
    demo()
