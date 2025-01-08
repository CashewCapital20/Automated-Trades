# Automated Trades

Traditional trading methods can be time-intensive, struggle to adapt to rapidly shifting market conditions, and often result in inefficiencies. 

 🥜 **Cashew Capital Fund** is a startup investment management fund interested in using ML to address this gap.

**Our Objective:** Design a machine learning algorithm that identifies trading opportunities through technical analysis and autonomously determine the best times to enter and exit for any particular stock.

## Data Preparation
Data Source: Benzinga Time-Series Data
- Historical (5-min candles): [Benzinga GET Bars](https://docs.benzinga.com/benzinga-apis/bars/get-bars)
- Real-Time (15-min delay): [Benzinga Delayed API](https://docs.benzinga.com/benzinga-apis/delayed-quote/get-quoteDelayed)

| Technical Indictator | Formula | Fine-tuned Parameters | Explanation |
| --------------- | --------------- | --------------- | --------------- | 
| Exponential Moving Averages (EMA) | ![ema_formula](https://github.com/user-attachments/assets/e3457d86-849c-4520-9d99-d345c9abbc83) <br> ![image](https://github.com/user-attachments/assets/eb738717-f40f-4162-9b2d-234f705df28a)| **N** = <br> 36-period & <br> 78-period <br> (3 and 6.5 hours)| Stabilizes trends for 2-day predictions <br> Better than standard spans of 12 & 26 days|
| Relative Strength Index (RSI) | ![rsi_formula](https://github.com/user-attachments/assets/a7145aeb-fadc-4123-b057-110bca19c629) | 9-period <br> (45 min) | Optimized for voilatile markets | 
| Moving Average Convergence Divergence (MACD) | ![macd_formula](https://github.com/user-attachments/assets/661af516-f058-4e74-9c74-059bf1d45190) | 27-period (Signal Line)  | Focuses on sustained signals, aligning with longer EMAs |
| Stochastic Oscillator | ![slowk_slow_d_formula](https://github.com/user-attachments/assets/ca331995-16ac-45e4-99c7-6e80971b4e6e) | 9-period (SlowK) <br> 3-period (SlowD) | (SlowK) Increases sensitivity to recent price action <br> (SlowD) Balances responsiveness with noise reduction |

## Algorithmic Approach

**Features:** MACD, MACD-Hist, RSI, SlowK, SlowD <br>

**We choose a classification approach. Why?** <br>
Trading decisions are categorical: you either buy, sell, or hold. Since we want an approach that is (1) easy to interpret and (2) quick to implement (for quicker testing and given limited timeframe), classification was the way to go! <br><br> Perfect for high frequency trading! ✨

---
**Method:** Create a label called “signal”  that represents whether we should buy or sell a stock based on its price over the next 2 days
- Strong sell signal: -2
- Weak sell signal: -1
- Hold signal: 0
- Weak buy signal: 1
- Strong buy signal: 2  
---

### Signal Type

| Signal Type   | Conditions                                                                                                                                  |
|---------------|------------------------------------------------------------------------------------------|
| **Strong Sell** | Min price ≤ 0.95 CP<br>Maximum price from now until the Min position ≤ 1.01 CP                    |
| **Weak Sell**   | Min price ≤ 0.97 CP<br>Maximum price from now until the Min position ≤ 1.01 CP                    |
| **Strong Buy**  | Max price ≥ 1.05 CP<br>Minimum price from now until the Max position ≥ 0.99 CP                   |
| **Weak Buy**    | Max price ≥ 1.03 CP<br>Minimum price from now until the Max position ≥ 0.99 CP                   |
| **Hold**        | Not Applicable                                     |

---

### Legend

- **CP** = Current Price
- **Min** = Min price over 2 days
- **Max** = Max price over 2 days
- **Threshold** = 5%
- **Future_period** = 155
- **Threshold_weak** = 3%
- **Min_diff** = 1%



## NoSQL Database 
Since our dataset updates daily, we used MongoDB to store our data on the cloud (better accessibility ✅) The database was organized into 3 categorical collections:
```
├── Historical Data/
├── EMA-78 Data/
│     └── AAPL-78
│     └── MSFT-78
│     └── TSLA-78
│     └── ...
├── Market Logs/
```

**Historical Data:** Stores historical stock data for the last 6 months, with 5-minute candlestick intervals (this is what the model is trained on)

**EMA-78 Data:** Stores 78 rows of past data needed to compute the technical indictator during real-time excutation

**Market Logs:** Stores logs of model executation (buy or sell). The schema is as follows:
- Timestamp 
- Trade Type 
- Monetary Metrics (e.g., trader’s funds and stock prices)
- Volume


## Signal Sample of NVDA
![nvda](https://github.com/user-attachments/assets/3bb16aa9-dcc1-4daf-b1d4-e4dc3017dbb6)



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
