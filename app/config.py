import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv(".env.development.local")

# Print all environment variables
for key, value in os.environ.items():
    print(f"{key}: {value}")

# Optionally, print specific environment variables
print("POSTGRES_URL:", os.getenv("POSTGRES_URL"))
