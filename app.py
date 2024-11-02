import gradio as gr
from fetch_load_mongo import prepare_data
from datetime import datetime, timedelta
from real_time_trading import real_time_trading

# placeholder for the model
def stock_recommendation(stock_symbol):
    # Replace this with actual prediction logic
    predicted_action = "Buy"  # Example prediction
    return f"Recommendation for {stock_symbol}: {predicted_action}"

def train_model(stocks):
    models = []
    start_date = (datetime.now() - timedelta(days=357)).strftime('%Y-%m-%d')
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    for symbol in stocks:
        df = prepare_data(symbol, start_date, end_date)
        models.append(df)
        
    return f"Successfully trained the models for {stocks}"

# End of day portfoio metrics
# Download csv of market logs
  
    
# front end interface
with gr.Blocks() as demo:
    gr.Markdown("#Automated Trading (DEMO)")
    
    stock1 = gr.Textbox(label="Stock #1 Symbol")
    stock2 = gr.Textbox(label="Stock #2 Symbol")
    stock3 = gr.Textbox(label="Stock #3 Symbol")
    
    train_model_button = gr.Button("Train Model")
    
    output = gr.Textbox(label="Recommendation")
    
    train_model_button.click(train_model, inputs=[stock1, stock2, stock3], outputs=output)

demo.launch(share=False)

def trading_interface(symbol):
    # Run the real-time trading for the specified stock and duration
    result = real_time_trading(symbol)
    return result