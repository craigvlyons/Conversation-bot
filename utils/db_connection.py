import pymongo
import os
from dotenv import load_dotenv
import requests
import json
from urllib.parse import quote_plus

load_dotenv(override=True) 

def get_mongo_client():
    DB_USERNAME = os.getenv("DB_USERNAME", "devopsAgent")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    # Properly escape username and password
    username = quote_plus(DB_USERNAME)
    password = quote_plus(DB_PASSWORD)

    # Format the connection string
    con = (
        f"mongodb+srv://{username}:{password}"
        "@devopsfunctionap-cosmosdbformongodb-adf4.global.mongocluster.cosmos.azure.com/"
        "?ssl=true&tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false"
    )
    
    client = pymongo.MongoClient(con)
    return client

# Example usage
def main():
    client = get_mongo_client()
    print("MongoDB client created successfully.")
    
    # Test connection by listing databases
    try:
        dbs = client.list_database_names()
        print("Databases:", dbs)
    except Exception as e:
        print("Error connecting to MongoDB:", e)


if __name__ == "__main__":
    main()
    
