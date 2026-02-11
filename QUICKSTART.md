# Quick Start Guide

Get up and running with the Instagram Service in 5 minutes!

## Prerequisites

- Python 3.7+
- Docker and Docker Compose
- Git

## Step-by-Step Setup

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt
```

### 2. Start LocalStack

```bash
# Start LocalStack services
docker-compose up -d

# Verify it's running
docker ps
```

### 3. Initialize Resources

```bash
# Wait a few seconds for LocalStack to be ready, then:
python scripts/setup.py
```

You should see:
```
Creating S3 bucket...
Bucket instagram-images-bucket created successfully
Creating DynamoDB table...
Table instagram-images created successfully

✓ LocalStack resources initialized successfully!
```

### 4. Test the Setup

```bash
# Run tests to verify everything works
pytest -v
```

All tests should pass! ✓

### 5. Try the API

Run the demo script:

```bash
python examples/api_demo.py
```

This will demonstrate all API operations:
- Upload an image
- List images
- Filter by user and tags
- Download an image
- Delete an image

## Alternative: Use Makefile

For convenience, you can use the Makefile:

```bash
# Install dependencies
make install

# Start LocalStack and initialize resources
make start

# Run tests
make test

# Run tests with coverage
make test-cov

# Stop LocalStack
make stop

# Clean up everything
make reset
```

## Manual API Testing

### Upload an Image

```bash
# Convert image to base64
IMAGE_DATA=$(base64 -i your_image.jpg | tr -d '\n')

# Upload via curl
curl -X POST http://localhost:4566/images \
  -H "Content-Type: application/json" \
  -d "{
    \"image\": \"$IMAGE_DATA\",
    \"user_id\": \"user123\",
    \"title\": \"My First Image\",
    \"tags\": [\"test\", \"demo\"]
  }"
```

Save the `image_id` from the response!

### List Images

```bash
# List all
curl http://localhost:4566/images

# Filter by user
curl "http://localhost:4566/images?user_id=user123"

# Filter by tag
curl "http://localhost:4566/images?tag=demo"
```

### Get Image

```bash
# Get metadata
curl http://localhost:4566/images/YOUR_IMAGE_ID

# Get presigned URL
curl "http://localhost:4566/images/YOUR_IMAGE_ID?url=true"

# Download image
curl "http://localhost:4566/images/YOUR_IMAGE_ID?download=true"
```

### Delete Image

```bash
curl -X DELETE http://localhost:4566/images/YOUR_IMAGE_ID
```

## Using AWS CLI

```bash
# Configure for LocalStack
export AWS_ENDPOINT=http://localhost:4566
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test

# List S3 buckets
aws --endpoint-url=$AWS_ENDPOINT s3 ls

# View DynamoDB table
aws --endpoint-url=$AWS_ENDPOINT dynamodb scan \
  --table-name instagram-images

# View items in S3
aws --endpoint-url=$AWS_ENDPOINT s3 ls s3://instagram-images-bucket/
```

## Troubleshooting

### LocalStack won't start

```bash
# Check Docker
docker ps

# Check logs
docker-compose logs

# Restart
docker-compose restart
```

### Tests fail

```bash
# Ensure LocalStack is running
docker ps | grep localstack

# Reinstall dependencies
pip install -r requirements.txt

# Run with verbose output
pytest -v -s
```

### Port 4566 already in use

```bash
# Find what's using the port
lsof -i :4566

# Or change the port in docker-compose.yml
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the code in [src/](src/)
- Review tests in [tests/](tests/)
- Customize configuration in [.env](.env)

## Need Help?

- Check the [README.md](README.md) for detailed documentation
- Review the [examples/](examples/) for more code samples
- Create an issue in the repository

Happy coding! 🚀
