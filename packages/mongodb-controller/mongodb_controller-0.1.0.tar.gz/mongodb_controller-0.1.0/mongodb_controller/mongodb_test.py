"""
Basic MongoDB connection test.
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient

def test_connection():
    """Test MongoDB connection using environment variables."""
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB connection string
    uri = os.getenv('MONGODB_URI')
    
    try:
        # Create client and test connection
        client = MongoClient(uri)
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        return client
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise
