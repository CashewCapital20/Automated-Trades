import os
import pymongo
import pandas as pd
from datetime import datetime 
from dotenv import load_dotenv

load_dotenv()
URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DATABASE_NAME')
COLL_NAME = os.getenv('COLLECTION_LOG')

client = pymongo.MongoClient(URI)
db = client[DB_NAME]
collection = db[COLL_NAME]
data = collection.find()
# print("Successfully exported training data")

def log_trade(timestamp, stock, initial_funds, trade_price, initial_quantity, quantity_traded, trade_type):
    total_cost = trade_price * quantity_traded
    remaining_quantity = initial_quantity
    funds_remaining = initial_funds
    
    if trade_type.lower() == "buy":
        remaining_quantity = initial_quantity + quantity_traded
        funds_remaining = initial_funds - total_cost
    elif trade_type.lower() == "sell":
        remaining_quantity = initial_quantity - quantity_traded
        funds_remaining = initial_funds + total_cost

    log_message = (
        f"{trade_type} {quantity_traded} shares of {stock} at ${trade_price:.2f} per share. "
        f"Initial quantity: {initial_quantity:.2f}. "
        f"Remaining quantity: {remaining_quantity:.2f}."
    )

    document = {"timestamp": timestamp,
    "initial_funds": initial_funds,
    "trade_price": trade_price,
    "initial_quantity": initial_quantity,
    "quantity_traded": quantity_traded,
    "remaining_quantity": remaining_quantity,
    "funds_remaining": funds_remaining,
    "log_message": log_message}

    collection.insert_one(document)
    print("Executed trade: ", log_message)

timestamp = datetime.now()
stock = "AAPL"
initial_price = 150.0
trade_price = 152.0
initial_funds = 10000.0  
quantity = 10
initial_quantity = 2234
trade_type = "sell" 

log_trade(timestamp, stock, initial_funds, trade_price, initial_quantity, quantity, trade_type)