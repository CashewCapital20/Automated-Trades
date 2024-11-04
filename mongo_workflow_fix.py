from pymongo import MongoClient

# Connect to MongoDB Atlas
client = MongoClient("your_mongodb_atlas_uri")
db = client["your_database_name"]
collection = db["your_collection_name"]

def fetch_stock_data(ticker):
    # Query to find all documents where 'ticker' field matches the given stock ticker
    query = {"ticker": ticker}
    results = collection.find(query)
    
    # Print or process each document
    for document in results:
        print(document)  # Or do any processing needed for each document

# Replace with the specific ticker you want to search
fetch_stock_data("AAPL")
