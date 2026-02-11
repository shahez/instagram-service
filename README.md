# Instagram-like Image Service

A scalable, serverless image upload and management service built with AWS services (API Gateway, Lambda, S3, DynamoDB) and Python 3.7+. This service supports multiple concurrent users and provides a complete REST API for image operations.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Local Development with LocalStack](#local-development-with-localstack)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Configuration](#configuration)

## ✨ Features

- **Upload images** with metadata (title, description, tags)
- **List images** with filtering by user ID or tags
- **View/Download images** with presigned URLs or direct download
- **Delete images** with automatic cleanup of metadata
- **Scalable architecture** using serverless AWS services
- **Local development** environment with LocalStack
- **Comprehensive test coverage** with unit and integration tests

## 🏗️ Architecture

The service uses the following AWS components:

- **API Gateway**: RESTful API endpoint management
- **Lambda Functions**: Serverless compute for each API operation
- **S3**: Object storage for images
- **DynamoDB**: NoSQL database for image metadata with GSI for filtering
  - Primary Key: `image_id`
  - Global Secondary Indexes:
    - `user_id-index`: Filter by user with sort by upload date
    - `tag-index`: Filter by tag with sort by upload date

## 📦 Prerequisites

- Python 3.7 or higher
- Docker and Docker Compose
- AWS CLI (configured)
- Git

## 🚀 Installation

1. **Clone the repository**:
```bash
cd /Users/shahenshah/Codebase/personal/instagram-service
```

2. **Create a virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## 🛠️ Local Development with LocalStack

LocalStack allows you to run AWS services locally for development and testing.

### What is LocalStack?

LocalStack is a fully functional local AWS cloud stack that provides an easy-to-use test/mocking framework for developing Cloud applications. It spins up a testing environment on your local machine that provides the same functionality as AWS.

### Starting LocalStack

1. **Start LocalStack services**:
```bash
docker-compose up -d
```

This will start:
- S3 on port 4566
- DynamoDB on port 4566
- API Gateway on port 4566
- Lambda on port 4566

2. **Verify LocalStack is running**:
```bash
docker ps
```

You should see the `instagram-localstack` container running.

3. **Initialize AWS resources**:
```bash
# Using Python script
python scripts/setup.py

# OR using bash script
chmod +x scripts/init-localstack.sh
./scripts/init-localstack.sh
```

This creates:
- S3 bucket: `instagram-images-bucket`
- DynamoDB table: `instagram-images` with GSI indexes

### Using AWS CLI with LocalStack

```bash
# Set endpoint URL for LocalStack
export AWS_ENDPOINT=http://localhost:4566
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test

# List S3 buckets
aws --endpoint-url=$AWS_ENDPOINT s3 ls

# List DynamoDB tables
aws --endpoint-url=$AWS_ENDPOINT dynamodb list-tables

# Scan DynamoDB table
aws --endpoint-url=$AWS_ENDPOINT dynamodb scan --table-name instagram-images
```

### Stopping LocalStack

```bash
docker-compose down
```

To remove all data:
```bash
docker-compose down -v
```

## 📚 API Documentation

### Base URL
```
Local: http://localhost:4566
Production: https://api.your-domain.com
```

### 1. Upload Image

Upload an image with metadata.

**Endpoint**: `POST /images`

**Request Body**:
```json
{
  "image": "base64_encoded_image_data",
  "user_id": "user123",
  "title": "Beautiful Sunset",
  "description": "A stunning sunset at the beach",
  "tags": ["sunset", "nature", "beach"],
  "content_type": "image/jpeg"
}
```

**Required Fields**:
- `image` (string): Base64 encoded image data
- `user_id` (string): ID of the user uploading the image

**Optional Fields**:
- `title` (string): Image title
- `description` (string): Image description
- `tags` (array): Array of tags
- `content_type` (string): MIME type (default: "image/jpeg")

**Response** (201 Created):
```json
{
  "message": "Image uploaded successfully",
  "image_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "metadata": {
    "image_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "user_id": "user123",
    "title": "Beautiful Sunset",
    "description": "A stunning sunset at the beach",
    "tags": ["sunset", "nature", "beach"],
    "upload_date": "2026-02-11T10:30:00.000000",
    "content_type": "image/jpeg",
    "size": 153600
  }
}
```

**Example with cURL**:
```bash
# Convert image to base64
IMAGE_BASE64=$(base64 -i image.jpg)

# Upload image
curl -X POST http://localhost:4566/images \
  -H "Content-Type: application/json" \
  -d '{
    "image": "'"$IMAGE_BASE64"'",
    "user_id": "user123",
    "title": "Test Image",
    "tags": ["test"]
  }'
```

**Example with Python**:
```python
import requests
import base64
import json

# Read and encode image
with open('image.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Upload
response = requests.post(
    'http://localhost:4566/images',
    json={
        'image': image_data,
        'user_id': 'user123',
        'title': 'Test Image',
        'tags': ['test']
    }
)

print(response.json())
```

### 2. List Images

Retrieve a list of images with optional filtering.

**Endpoint**: `GET /images`

**Query Parameters**:
- `user_id` (optional): Filter by user ID
- `tag` (optional): Filter by tag

**Note**: You can use either `user_id` OR `tag`, but not both simultaneously.

**Response** (200 OK):
```json
{
  "count": 2,
  "images": [
    {
      "image_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "user_id": "user123",
      "title": "Beautiful Sunset",
      "description": "A stunning sunset at the beach",
      "tags": ["sunset", "nature", "beach"],
      "upload_date": "2026-02-11T10:30:00.000000",
      "content_type": "image/jpeg",
      "size": 153600
    },
    {
      "image_id": "b2c3d4e5-f6g7-8901-bcde-fg2345678901",
      "user_id": "user123",
      "title": "Mountain View",
      "description": "Snow-capped mountains",
      "tags": ["mountain", "nature", "snow"],
      "upload_date": "2026-02-11T11:45:00.000000",
      "content_type": "image/jpeg",
      "size": 204800
    }
  ]
}
```

**Examples**:

```bash
# List all images
curl http://localhost:4566/images

# Filter by user_id
curl http://localhost:4566/images?user_id=user123

# Filter by tag
curl http://localhost:4566/images?tag=sunset
```

### 3. Get/Download Image

Retrieve image metadata or download image data.

**Endpoint**: `GET /images/{image_id}`

**Path Parameters**:
- `image_id` (required): The unique ID of the image

**Query Parameters**:
- `download=true`: Get base64 encoded image data
- `url=true`: Get presigned S3 URL (valid for 1 hour)

**Response - Metadata Only** (200 OK):
```json
{
  "image_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "metadata": {
    "image_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "user_id": "user123",
    "title": "Beautiful Sunset",
    "upload_date": "2026-02-11T10:30:00.000000",
    "tags": ["sunset", "nature"]
  }
}
```

**Response - With Download** (200 OK):
```json
{
  "image_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "image_data": "base64_encoded_image_data_here...",
  "content_type": "image/jpeg",
  "metadata": { ... }
}
```

**Response - With Presigned URL** (200 OK):
```json
{
  "image_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "url": "https://instagram-images-bucket.s3.amazonaws.com/...",
  "metadata": { ... }
}
```

**Examples**:

```bash
# Get metadata only
curl http://localhost:4566/images/a1b2c3d4-e5f6-7890-abcd-ef1234567890

# Download image data
curl http://localhost:4566/images/a1b2c3d4-e5f6-7890-abcd-ef1234567890?download=true

# Get presigned URL
curl http://localhost:4566/images/a1b2c3d4-e5f6-7890-abcd-ef1234567890?url=true
```

**Python Example - Download and Save**:
```python
import requests
import base64

image_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
response = requests.get(
    f'http://localhost:4566/images/{image_id}?download=true'
)

data = response.json()
image_bytes = base64.b64decode(data['image_data'])

with open('downloaded_image.jpg', 'wb') as f:
    f.write(image_bytes)
```

### 4. Delete Image

Delete an image and its metadata.

**Endpoint**: `DELETE /images/{image_id}`

**Path Parameters**:
- `image_id` (required): The unique ID of the image to delete

**Response** (200 OK):
```json
{
  "message": "Image deleted successfully",
  "image_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Error Response** (404 Not Found):
```json
{
  "error": "Image not found"
}
```

**Example**:
```bash
curl -X DELETE http://localhost:4566/images/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### Error Responses

All endpoints may return the following error responses:

**400 Bad Request**:
```json
{
  "error": "Descriptive error message"
}
```

**404 Not Found**:
```json
{
  "error": "Image not found"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Internal server error: detailed message"
}
```

## 🧪 Testing

The project includes comprehensive unit and integration tests.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_upload_image.py

# Run with verbose output
pytest -v

# View coverage report
open htmlcov/index.html
```

### Test Structure

- `test_upload_image.py`: Tests for image upload functionality
- `test_list_images.py`: Tests for image listing with filters
- `test_get_image.py`: Tests for image retrieval
- `test_delete_image.py`: Tests for image deletion
- `test_integration.py`: End-to-end integration tests

### Test Coverage

The test suite covers:
- ✅ Successful operations
- ✅ Missing required fields
- ✅ Invalid input data
- ✅ Resource not found scenarios
- ✅ Service failures (S3, DynamoDB)
- ✅ Complete workflows (upload → list → get → delete)
- ✅ Filtering by user_id and tags
- ✅ Edge cases and error handling

## 📁 Project Structure

```
instagram-service/
├── src/
│   ├── __init__.py
│   ├── config.py                 # Configuration and environment variables
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── upload_image.py       # Upload image Lambda handler
│   │   ├── list_images.py        # List images Lambda handler
│   │   ├── get_image.py          # Get/download image Lambda handler
│   │   └── delete_image.py       # Delete image Lambda handler
│   └── utils/
│       ├── __init__.py
│       ├── dynamodb_utils.py     # DynamoDB operations
│       └── s3_utils.py           # S3 operations
├── tests/
│   ├── __init__.py
│   ├── test_upload_image.py
│   ├── test_list_images.py
│   ├── test_get_image.py
│   ├── test_delete_image.py
│   └── test_integration.py
├── scripts/
│   ├── init-localstack.sh        # LocalStack initialization script
│   └── setup.py                  # Python setup script
├── docker-compose.yml            # LocalStack Docker configuration
├── requirements.txt              # Python dependencies
├── pytest.ini                    # Pytest configuration
├── .env.example                  # Environment variables template
├── .gitignore
└── README.md                     # This file
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test

# Service Configuration
DYNAMODB_TABLE=instagram-images
S3_BUCKET=instagram-images-bucket

# LocalStack
LOCALSTACK_ENDPOINT=http://localhost:4566
USE_LOCALSTACK=true
```

### DynamoDB Schema

**Table Name**: `instagram-images`

**Primary Key**: `image_id` (String)

**Attributes**:
- `image_id`: Unique identifier (UUID)
- `user_id`: User who uploaded the image
- `title`: Image title
- `description`: Image description
- `tags`: Array of tags
- `tag`: First tag (for GSI)
- `upload_date`: ISO 8601 timestamp
- `content_type`: MIME type
- `size`: File size in bytes

**Global Secondary Indexes**:
1. **user_id-index**
   - Partition Key: `user_id`
   - Sort Key: `upload_date`
   
2. **tag-index**
   - Partition Key: `tag`
   - Sort Key: `upload_date`

## 🚀 Deployment to AWS

To deploy to actual AWS (not LocalStack):

1. **Update environment variables**:
```env
USE_LOCALSTACK=false
# Remove LOCALSTACK_ENDPOINT
# Set actual AWS credentials
```

2. **Create AWS resources**:
```bash
python scripts/setup.py
```

3. **Deploy Lambda functions** using AWS SAM, Serverless Framework, or manually:

Example with AWS SAM:
```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  UploadImageFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src.handlers.upload_image.lambda_handler
      Runtime: python3.9
      Events:
        UploadAPI:
          Type: Api
          Properties:
            Path: /images
            Method: POST
```

4. **Deploy**:
```bash
sam build
sam deploy --guided
```

## 📝 Best Practices

1. **Error Handling**: All handlers include comprehensive error handling
2. **Validation**: Input validation on all endpoints
3. **Scalability**: Serverless architecture scales automatically
4. **Security**: Use IAM roles for Lambda execution
5. **Monitoring**: Enable CloudWatch logs for all Lambda functions
6. **Testing**: 85%+ test coverage with unit and integration tests

## 🔗 Useful Resources

- [LocalStack Documentation](https://docs.localstack.cloud/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)

## 📄 License

This project is for educational purposes.

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 🐛 Troubleshooting

### LocalStack not starting
```bash
# Check Docker is running
docker ps

# Check logs
docker-compose logs localstack

# Restart services
docker-compose restart
```

### Tests failing
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Install test dependencies
pip install -r requirements.txt

# Run tests with verbose output
pytest -v -s
```

### AWS CLI issues with LocalStack
```bash
# Ensure endpoint URL is set
export AWS_ENDPOINT=http://localhost:4566

# Verify LocalStack is accessible
curl http://localhost:4566/_localstack/health
```

## 📧 Support

For issues and questions, please create an issue in the repository.
