import gradio as gr
from real_time_trading import real_time_trading

def trading_interface(symbol):
    # Run the real-time trading for the specified stock and duration
    result = real_time_trading(symbol)
    return result

iface = gr.Interface(
    fn = trading_interface,
    inputs = [
        gr.inputs.Textbox(label = "Stock Symbol", placeholder = "e.g., NVDA"),
        gr.inputs.Textbox(label = "Stock Symbol", placeholder = "e.g., GOOG"),
        gr.inputs.Textbox(label = "Stock Symbol", placeholder = "e.g., AAPL")
    ],
    outputs = "dataframe",
    title = "Real-Time Stock Trading Interface",
    description = "Input three stock symbols to run the real-time trading script.",
    submit_button = gr.Button("Submit")
    #submit_button.click(stock_recommendation, inputs=[stock_symbol], outputs=output)
)

iface.launch()

    
    #output = gr.Textbox(label="Recommendation")
