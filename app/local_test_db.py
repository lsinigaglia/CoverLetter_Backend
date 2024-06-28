from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/coverletter"
engine = create_engine(DATABASE_URL)

try:
    conn = engine.connect()
    print("Database connection was successful!")
except Exception as e:
    print("Failed to connect to the database:")
    print(e)
finally:
    conn.close()
