Introduction
Back end Fast API
Cover Letter Generator

Prerequisites
Python 3.x
pip (Python package installer)
Virtual environment (optional but recommended)
PostgreSQL database
Setup
1. Clone the Repository
bash
Copy code
git clone https://github.com/your-username/your-repository.git
cd your-repository
2. Create and Activate Virtual Environment
On Windows:

bash
Copy code
python -m venv venv
venv\Scripts\activate
On macOS/Linux:

bash
Copy code
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
bash
Copy code
pip install -r requirements.txt
Database Setup
1. Configure Database
In database.py, ensure the database connection string is set correctly,
change it according to to your database and credentials: 


DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/trap"
2. Initialize the Database

Uncomment the #init_db() line in your code to generate the tables. Run the server once to initialize the database:


# init_db()
Running the Server
1. Set Environment Variables
You may need to set environment variables depending on your setup. Here's how to set the DATABASE_URL:

On Windows:


set DATABASE_URL=postgresql://postgres:postgres@localhost:5433/trap
On macOS/Linux:


export DATABASE_URL=postgresql://postgres:postgres@localhost:5433/trap
2. Run the Server
Use uvicorn to run your FastAPI application:

try both the following commands. Be sure to stay in the root of the project
python -m app.main
uvicorn app.main:app --reload
The server should be running on http://127.0.0.1:8000.



Using Swagger for API Documentation
Swagger UI is available to visualize and interact with your API.

1. Access Swagger UI
Navigate to http://127.0.0.1:8000/docs in your web browser.

2. Interact with API
Use the Swagger UI to test and interact with your API endpoints. The documentation should provide details on each endpoint, parameters, and expected responses.