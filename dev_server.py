"""
Simple HTTP server wrapper for Lambda handlers (development/testing only)
Run this to test the Lambda handlers via HTTP without deploying to API Gateway
"""
from flask import Flask, request, jsonify
import json
from src.handlers.upload_image import lambda_handler as upload_handler
from src.handlers.list_images import lambda_handler as list_handler
from src.handlers.get_image import lambda_handler as get_handler
from src.handlers.delete_image import lambda_handler as delete_handler

app = Flask(__name__)


@app.route('/images', methods=['POST'])
def upload_image():
    """Upload image endpoint"""
    event = {
        'body': json.dumps(request.json) if request.json else '{}'
    }
    response = upload_handler(event, None)
    return jsonify(json.loads(response['body'])), response['statusCode']


@app.route('/images', methods=['GET'])
def list_images():
    """List images endpoint"""
    event = {
        'queryStringParameters': dict(request.args) if request.args else None
    }
    response = list_handler(event, None)
    return jsonify(json.loads(response['body'])), response['statusCode']


@app.route('/images/<image_id>', methods=['GET'])
def get_image(image_id):
    """Get/download image endpoint"""
    event = {
        'pathParameters': {'image_id': image_id},
        'queryStringParameters': dict(request.args) if request.args else None
    }
    response = get_handler(event, None)
    return jsonify(json.loads(response['body'])), response['statusCode']


@app.route('/images/<image_id>', methods=['DELETE'])
def delete_image(image_id):
    """Delete image endpoint"""
    event = {
        'pathParameters': {'image_id': image_id}
    }
    response = delete_handler(event, None)
    return jsonify(json.loads(response['body'])), response['statusCode']


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'instagram-service'}), 200


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  Instagram Service - Development HTTP Server")
    print("="*60)
    print("\nServer running at: http://127.0.0.1:5001")
    print("\nAvailable endpoints:")
    print("  POST   http://127.0.0.1:5001/images")
    print("  GET    http://127.0.0.1:5001/images")
    print("  GET    http://127.0.0.1:5001/images/{image_id}")
    print("  DELETE http://127.0.0.1:5001/images/{image_id}")
    print("  GET    http://127.0.0.1:5001/health")
    print("\nUsing LocalStack S3 and DynamoDB at: http://localhost:4566")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
