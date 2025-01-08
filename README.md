# Automated Trades

Traditional trading methods can be time-intensive, struggle to adapt to rapidly shifting market conditions, and often result in inefficiencies. 

 🥜 **Cashew Capital Fund** is a startup investment management fund interested in using ML to address this gap.

**Our Objective:** Design a machine learning algorithm that identifies trading opportunities through technical analysis and autonomously determine the best times to enter and exit for any particular stock.

## Methodology

### Data Preparation
Data Source: Benzinga Time-Series Data
- Historical (5-min candles): [Benzinga GET Bars](https://docs.benzinga.com/benzinga-apis/bars/get-bars)
- Real-Time (15-min delay): [Benzinga Delayed API](https://docs.benzinga.com/benzinga-apis/delayed-quote/get-quoteDelayed)

| Technical Indictator | Formula | Fine-tuned Parameters | Explanation |
| --------------- | --------------- | --------------- | --------------- | 
| Exponential Moving Averages (EMA) | ![ema_formula](https://github.com/user-attachments/assets/e3457d86-849c-4520-9d99-d345c9abbc83) | 36-period <br> 78-period <br> (3 and 6.5 hours)| Stabilizes trends for 2-day predictions <br> Better than standard spans of 12 & 26 days|
| Relative Strength Index (RSI) | ![rsi_formula](https://github.com/user-attachments/assets/a7145aeb-fadc-4123-b057-110bca19c629) | 9-period <br> (45 min) | Optimized for voilatile markets | 
| Moving Average Convergence Divergence (MACD) | ![macd_formula](https://github.com/user-attachments/assets/661af516-f058-4e74-9c74-059bf1d45190) | 27-period (Signal Line)  | Focuses on sustained signals, aligning with longer EMAs |
| Stochastic Oscillator | ![slowk_slow_d_formula](https://github.com/user-attachments/assets/ca331995-16ac-45e4-99c7-6e80971b4e6e) | 9-period (SlowK) <br> 3-period (SlowD) | (SlowK) Increases sensitivity to recent price action <br> (SlowD) Balances responsiveness with noise reduction |

## Installing Dependencies

To install the necessary dependencies for this project, follow these steps:

1. **Install the dependencies**:  
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify installation**:  
   ```bash
   pip list
   ```

## Credits and Acknowledgements 
Special thanks to Swathi Senthil, George Abu Daoud, Bharath Venkataraman, and Boshen Parthasarathy for the feedback and mentorship.

**Tools/Libraries:** Google Colab, VSCode, Scikit-learn, MongoDB, Benzinga
