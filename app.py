import logging
import time
import numpy as np
import pandas as pd
import gradio as gr
import matplotlib.pyplot as plt
from datetime import datetime
import pytz
from fetch_load_mongo import DataFetcher
from train_model import TradingModel
from real_time_trading import RealTimeTrader

# Initialize the RealTimeTrader instance
real_time_traders = {}

def is_market_open():
    # Check if the market is open
    now = datetime.now(pytz.timezone("America/New_York"))
    current_day = now.weekday()

    # Check if it's a weekday (Monday to Friday) and between 9:30 AM to 4 PM
    if current_day >= 0 and current_day <= 4 and (9, 30) <= (now.hour, now.minute) < (16, 0):
        return True
    return False

def stock_recommendation(stock1, stock2, stock3, stock4, stock5):
    # Get real-time recommendations for stocks
    if not is_market_open():
        return "Recommendations are unavailable outside market hours (Weekdays 9:30 AM - 4 PM)."

    stock_symbols = [s.upper() for s in [stock1, stock2, stock3, stock4, stock5] if s]
    recommendations = []
    price_data = {}

    for symbol in stock_symbols:
        try:
            if symbol not in real_time_traders:
                real_time_traders[symbol] = RealTimeTrader(symbol)

            trader = real_time_traders[symbol]

            # fetch data to make predictions
            latest_data = trader.fetch_latest_data()
            if latest_data.empty:
                raise ValueError(f"No data fetched for {symbol}")

            prepared_data = trader.trading_model.calculate_indicators(latest_data)
            if len(prepared_data) == 0:
                raise ValueError(f"Insufficient data for {symbol}")

            latest_row = prepared_data.iloc[-1]
            X_real_time = pd.DataFrame({
                'macd': [latest_row['macd']],
                'macd_hist': [latest_row['macd_hist']],
                'rsi': [latest_row['rsi']],
                'slowk': [latest_row['slowk']],
                'slowd': [latest_row['slowd']]
            })

            prediction = trader.model.predict(X_real_time)[0]
            trade_decision = trader.trade_decision(prediction)
            recommendations.append(f"{symbol}: {trade_decision}")

            # collect price data
            price_data[symbol] = latest_data['close']
        except Exception as e:
            recommendations.append(f"{symbol}: Error - {str(e)}")

    return "\n".join(recommendations)

def train_model(stock1, stock2, stock3, stock4, stock5):
    # Trains models for each stock symbol provided
    data_fetcher = DataFetcher()
    training_output = []

    stock_symbols = [s.upper() for s in [stock1, stock2, stock3, stock4, stock5] if s]

    for symbol in stock_symbols:
        try:         
            # retrieve real time data
            if symbol not in real_time_traders:
                real_time_traders[symbol] = RealTimeTrader(symbol)

            trader = real_time_traders[symbol]

            # fetch historical data and train the trading model
            df = data_fetcher.prepare_data(symbol)
            if df.empty:
                raise ValueError(f"No data available for {symbol}")
            
            trader.trading_model.create_model()  # Assuming this saves the model
            training_output.append(f"Model trained for {symbol}")
        except Exception as e:
            logging.error(f"Error training model for {symbol}: {str(e)}")
            training_output.append(f"Error training model for {symbol}: {str(e)}")

    return "\n".join(training_output)

#--------------------------------#
# Start & Stop Trading
#--------------------------------#

fig = None
is_trading = False
def start_trading(stock1, stock2, stock3, stock4, stock5):
    global is_trading, fig
    is_trading = True

    stock_symbols = [s.upper() for s in [stock1, stock2, stock3, stock4, stock5] if s]
    num_stocks = len(stock_symbols)
    fig, axs = plt.subplots(num_stocks, 1, figsize=(10, 6 * num_stocks), sharex=True)
    message = "Trading started and updating plot in real-time."
    
    curr_prices = {symbol: [] for symbol in stock_symbols}
    
    while is_trading:
        if not is_market_open():
            return "Recommendations are unavailable outside market hours (Weekdays 9:30 AM - 4 PM).", None

        for idx, symbol in enumerate(stock_symbols):
            try:
                if symbol not in real_time_traders:
                    real_time_traders[symbol] = RealTimeTrader(symbol)

                trader = real_time_traders[symbol]

                # Fetch data to make predictions
                latest_data = trader.fetch_latest_data()
                if latest_data.empty:
                    raise ValueError(f"No data fetched for {symbol}")

                # Perform the trading model logic
                prepared_data = trader.trading_model.calculate_indicators(latest_data)
                if len(prepared_data) == 0:
                    raise ValueError(f"Insufficient data for {symbol}")

                latest_row = prepared_data.iloc[-1]
                X_real_time = pd.DataFrame({
                    "macd": [latest_row["macd"]],
                    "macd_hist": [latest_row["macd_hist"]],
                    "rsi": [latest_row["rsi"]],
                    "slowk": [latest_row["slowk"]],
                    "slowd": [latest_row["slowd"]],
                })

                prediction = trader.model.predict(X_real_time)[0]
                trade_decision = trader.trade_decision(prediction)

                # Update open prices and x_data for plotting
                price = float(latest_data["close"].iloc[-1])
                timestamp = latest_data["time"].iloc[-1]
                
                if not curr_prices[symbol] or curr_prices[symbol][-1][0] != timestamp:
                            curr_prices[symbol].append((timestamp, price))
                                
                print("============== IDX: ", idx, " Stock: ", symbol, " Price:", curr_prices[symbol])

                # Log trade action if necessary
                trade_price = latest_data["close"].iloc[0]
                trader.log_trade_action(trade_decision, latest_data["close"].iloc[0], trade_price)
                logging.info(f"Logged trade action: {trade_decision} for {symbol}")

                # Clear and update the corresponding subplot
                axs[idx].clear()
                timestamps, prices = zip(*curr_prices[symbol])  # Unpack dateTime and price
                axs[idx].plot(timestamps, prices, label=f"{symbol} Price")
                axs[idx].set_title(f"Stock: {symbol}")
                axs[idx].set_ylabel("Price")
                axs[idx].legend()

            except Exception as e:
                logging.error(f"Error trading {symbol}: {str(e)}")
                axs[idx].set_title(f"Error: {symbol}")
                axs[idx].set_ylabel("Price")

        axs[-1].set_xlabel("Time")  
        axs[-1].tick_params(axis="x", rotation=45)
        time.sleep(5)  # Delay to simulate real-time updates
        yield message, fig

    # Final return to provide consistent outputs after stopping
    return message, fig

# Function to stop trading and freeze the current graph
def stop_trading():
    global is_trading, fig
    is_trading = False
    recommendations = "Trading stopped."

    if fig is None:
        fig = plt.subplots(figsize=(10, 6))
    
    return recommendations, fig 

# Gradio front-end interface
with gr.Blocks() as demo:
    gr.Markdown("# Automated Trading v1.0")
    with gr.Row():
        with gr.Column(scale=1, min_width=300):
            stock1 = gr.Textbox(label="Stock #1 Symbol")
            stock2 = gr.Textbox(label="Stock #2 Symbol")
            stock3 = gr.Textbox(label="Stock #3 Symbol")
            stock4 = gr.Textbox(label="Stock #4 Symbol")
            stock5 = gr.Textbox(label="Stock #5 Symbol")
            
            training_output = gr.Textbox(label="Training Output", placeholder="Model training result will appear here.")
            train_model_btn = gr.Button("Train Model")
            train_model_btn.click(train_model, inputs=[stock1, stock2, stock3, stock4, stock5], outputs=training_output)
        
            recommendation_output = gr.Textbox(label="Recommendations")
            recommend_btn = gr.Button("Get Recommendation", variant="secondary")
            recommend_btn.click(stock_recommendation, inputs=[stock1, stock2, stock3, stock4, stock5], outputs=recommendation_output)
        
        with gr.Column(variant="panel", scale=2, min_width=300):
            plot_output = gr.Plot()
            action_output = gr.Textbox(label="", placeholder="Trading status will appear here.")

            with gr.Row():
                start_trades_btn = gr.Button("Start trading", variant="primary")
                stop_trades_btn = gr.Button("Stop trading")
    
                start_trades_btn.click(
                    start_trading,
                    inputs=[stock1, stock2, stock3, stock4, stock5],
                    outputs=[action_output, plot_output],
                )
                
                stop_trades_btn.click(
                    stop_trading, 
                    inputs=[], 
                    outputs=[action_output, plot_output]
                )
        with gr.Column(scale=1, min_width=100):
            clear_btn = gr.Button("Clear MongoDB Collections")
            clear_btn.click(DataFetcher.drop_collections)

# Launch Gradio interface
demo.launch(share=False)