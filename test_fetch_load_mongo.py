from fetch_load_mongo import prepare_data

# Sample Test 
symbol = 'NVDA'
date_from = '2023-10-01'
date_to = '2024-10-27'

df = prepare_data(symbol, date_from, date_to)
if not df.empty:
    print("Successfully uploaded data!")
else:
    print("Failed to upload data.")