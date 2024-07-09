import os
from dotenv import load_dotenv
import boto3

test_user_id = 1

# Load environment variables from .env file
load_dotenv(".env.development.local")
# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)
s3_bucket_name = os.getenv('S3_BUCKET_NAME')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


# Print all environment variables
""" for key, value in os.environ.items():
    print(f"{key}: {value}")

# Optionally, print specific environment variables
print("POSTGRES_URL:", os.getenv("POSTGRES_URL")) """

#SETTING FOR VERCEL
""" {
  "rewrites": [
    { "source": "/(.*)", "destination": "app/api/main.py" }
  ],
  "functions": {
    "app/api/main.py": {
      "maxDuration": 60
    }
  }
}
 """