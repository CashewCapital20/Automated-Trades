import os
import requests
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DelayedStockQuote:
    def __init__(self):
        load_dotenv()  
        self.api_key = os.getenv('BENZINGA_APIKEY')  
        self.base_url = "https://api.benzinga.com/api/v1/quoteDelayed"
    
    def get_delayed_quote(self, symbols=None, isin=None, cik=None):
        querystring = {
            "token": self.api_key,
            "symbols":symbols
        }
        headers = {"accept": "application/json"}
        
        try:
            response = requests.get(self.base_url, headers=headers, params=querystring)
            if response.status_code == 200:
                data = response.json()
                quotes = data["quotes"][0]["quote"]
            
                extracted_data = {
                    "time": quotes.get('date'),
                    "open": quotes.get('open'),
                    "high": quotes.get('high'),
                    "low": quotes.get('low'),
                    "close": quotes.get('last'), 
                    "volume": quotes.get('volume'),
                    "dateTime": quotes.get('previousCloseDate') 
                }
                
                logging.info(f"Fetched and extracted data: {extracted_data}")
                return extracted_data
            else:
                logging.error(f"Failed to fetch data. Status code: {response.status_code}, Response: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while fetching data: {e}")
            return None


# Example usage
if __name__ == "__main__":
    benzinga_api = DelayedStockQuote()
    quote_data = benzinga_api.get_delayed_quote(symbols="NVDA")