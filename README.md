# Company Valuation with Python and Yahoo Finance

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)
[![yfinance](https://img.shields.io/badge/yfinance-latest-green)](https://pypi.org/project/yfinance/)
[![matplotlib](https://img.shields.io/badge/matplotlib-latest-orange)](https://matplotlib.org/)

This repository contains a Python script for performing comprehensive company valuations using data from the Yahoo Finance API. The script implements five commonly used valuation methods in financial analysis.

## 📋 Features

- **Discounted Cash Flow (DCF)** - Calculates company value based on projected future cash flows discounted to present value
- **Price to Earnings Ratio (P/E)** - Compares stock price to earnings per share
- **Price to Book Value (P/BV)** - Compares stock price to book value per share
- **EV/EBITDA** - Compares enterprise value to EBITDA (Earnings Before Interest, Taxes, Depreciation, and Amortization)
- **Comparable Companies (Market Multiples)** - Uses average valuation metrics from similar companies

## 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/ichsanfachris/company-valuation.git
cd company-valuation

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # For Linux/Mac
# or
venv\Scripts\activate     # For Windows

# Install dependencies
pip install -r requirements.txt
```

## 📦 Dependencies

- Python 3.7+
- pandas
- numpy
- yfinance
- matplotlib
- scipy

## 🚀 Usage

Run the main script:

```bash
python valuation.py
```

The script will prompt for input:
1. Company ticker symbol (e.g., AAPL for Apple, MSFT for Microsoft)
2. Whether to use comparable companies
3. If yes, enter ticker symbols for comparable companies (separated by commas)

### Example Usage

```
=== COMPANY VALUATION PROGRAM ===
Enter company ticker symbol (example: AAPL): MSFT
Do you want to use comparable companies? (y/n): y
Enter ticker symbols for comparable companies (separate with commas): AAPL, GOOGL, AMZN
```

The script will fetch financial data from Yahoo Finance, perform valuation calculations, and display the results in both tabular form and as a chart. The chart will be saved as a PNG file named after the company's ticker symbol.

## 📊 Valuation Methods

### 1. Discounted Cash Flow (DCF)

DCF calculates the intrinsic value of a company based on projected future cash flows discounted to present value.

```
DCF = ∑(CFt / (1+r)^t) + TV / (1+r)^n
```

Where:
- CFt: Cash Flow in year t
- r: Discount rate (typically WACC)
- TV: Terminal Value
- n: Number of projection years

### 2. Price to Earnings Ratio (P/E)

Compares the stock price to earnings per share.

```
P/E Ratio = Stock Price / Earnings per Share (EPS)
```

### 3. Price to Book Value (P/BV)

Compares the stock price to book value per share.

```
P/BV = Stock Price / Book Value per Share
```

### 4. EV/EBITDA

Compares Enterprise Value to EBITDA.

```
EV/EBITDA = Enterprise Value / EBITDA
```

Where:
- Enterprise Value = Market Cap + Total Debt - Cash
- EBITDA = Earnings Before Interest, Taxes, Depreciation, and Amortization

### 5. Comparable Companies (Market Multiples)

Uses average valuation metrics from similar companies to estimate the fair value of the target company.

## ⚠️ Limitations

- Availability and completeness of data through Yahoo Finance API varies for each company
- Companies from non-US markets may have less complete data
- For companies in local exchanges, use appropriate suffixes (e.g., `.JK` for Indonesia)
- Some companies may not have the required data for certain valuation methods
- Results are heavily dependent on the quality and accuracy of available financial data

## 📝 Important Notes

- This script is created for educational and research purposes
- Valuation results should not be the sole basis for investment decisions
- Consider consulting with a financial professional before making investment decisions
- Different valuation methods often produce different results - consider them as a range of possible values

## 🔄 Future Development

- [ ] Add more valuation methods
- [ ] Add support for alternative data sources
- [ ] Implement better error handling
- [ ] Add sensitivity analysis features
- [ ] Create web interface for easier use
- [ ] Support for exporting results to Excel or PDF formats

## 📜 License

MIT License

## 🤝 Contribution

Contributions are always welcome. Please feel free to fork this repository, make changes, and submit pull requests.
