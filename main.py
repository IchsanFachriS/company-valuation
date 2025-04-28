import pandas as pd
import numpy as np
import yfinance as yf
import datetime
import matplotlib.pyplot as plt
from scipy.stats import gmean

def get_financial_data(ticker_symbol):
    """
    Mengambil data keuangan perusahaan dari Yahoo Finance
    """
    try:
        company = yf.Ticker(ticker_symbol)
        
        # Mendapatkan data historis
        hist = company.history(period="1y")
        
        # Mendapatkan data keuangan
        income_stmt = company.income_stmt
        balance_sheet = company.balance_sheet
        cash_flow = company.cashflow
        
        # Mendapatkan info perusahaan
        info = company.info
        
        return {
            'company': company,
            'hist': hist,
            'income_stmt': income_stmt,
            'balance_sheet': balance_sheet,
            'cash_flow': cash_flow,
            'info': info
        }
    except Exception as e:
        print(f"Error getting data: {e}")
        return None

def dcf_valuation(financial_data, growth_rate=0.05, discount_rate=0.1, terminal_growth_rate=0.02, years=5):
    """
    Melakukan valuasi dengan metode Discounted Cash Flow
    """
    try:
        cash_flow = financial_data['cash_flow']
        
        # Mengambil Free Cash Flow terakhir
        # Biasanya dihitung sebagai: Operating Cash Flow - Capital Expenditures
        try:
            operating_cash_flow = cash_flow.loc['Operating Cash Flow'].iloc[-1]
            capital_expenditures = cash_flow.loc['Capital Expenditure'].iloc[-1]
            free_cash_flow = operating_cash_flow - abs(capital_expenditures)
        except:
            # Jika tidak tersedia, gunakan total kas operasi
            free_cash_flow = cash_flow.loc['Operating Cash Flow'].iloc[-1]
        
        # Memproyeksikan free cash flow untuk masa depan
        projected_cash_flows = []
        for i in range(1, years + 1):
            fcf = free_cash_flow * (1 + growth_rate) ** i
            projected_cash_flows.append(fcf)
        
        # Menghitung Terminal Value
        terminal_value = projected_cash_flows[-1] * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)
        
        # Menghitung Present Value dari setiap cash flow
        present_values = [cf / (1 + discount_rate) ** (i+1) for i, cf in enumerate(projected_cash_flows)]
        
        # Menghitung Present Value dari Terminal Value
        present_value_terminal = terminal_value / (1 + discount_rate) ** years
        
        # Total Enterprise Value
        enterprise_value = sum(present_values) + present_value_terminal
        
        # Menghitung Equity Value
        try:
            cash = financial_data['balance_sheet'].loc['Cash And Cash Equivalents'].iloc[-1]
            debt = financial_data['balance_sheet'].loc['Total Debt'].iloc[-1]
        except:
            # Jika tidak ada data spesifik, gunakan data tambahan
            cash = financial_data['balance_sheet'].loc['Cash And Short Term Investments'].iloc[-1] if 'Cash And Short Term Investments' in financial_data['balance_sheet'].index else 0
            debt = financial_data['balance_sheet'].loc['Long Term Debt'].iloc[-1] if 'Long Term Debt' in financial_data['balance_sheet'].index else 0
        
        equity_value = enterprise_value + cash - debt
        
        # Menghitung nilai per saham
        shares_outstanding = financial_data['info'].get('sharesOutstanding', 1)
        dcf_value_per_share = equity_value / shares_outstanding
        
        return {
            'enterprise_value': enterprise_value,
            'equity_value': equity_value,
            'dcf_value_per_share': dcf_value_per_share,
            'projected_cash_flows': projected_cash_flows,
            'present_values': present_values,
            'terminal_value': terminal_value
        }
    except Exception as e:
        print(f"Error in DCF valuation: {e}")
        return None

def pe_valuation(financial_data, target_companies=None):
    """
    Melakukan valuasi dengan metode Price to Earnings
    """
    try:
        # Mendapatkan EPS aktual perusahaan
        eps = financial_data['info'].get('trailingEPS')
        if not eps:
            # Jika tidak ada trailing EPS, hitung dari net income
            income_stmt = financial_data['income_stmt']
            net_income = income_stmt.loc['Net Income'].iloc[-1]
            shares_outstanding = financial_data['info'].get('sharesOutstanding', 1)
            eps = net_income / shares_outstanding
        
        # Jika ada target perusahaan pembanding, gunakan rata-rata P/E mereka
        if target_companies:
            pe_ratios = []
            for ticker in target_companies:
                try:
                    company = yf.Ticker(ticker)
                    pe_ratio = company.info.get('trailingPE')
                    if pe_ratio and pe_ratio > 0:
                        pe_ratios.append(pe_ratio)
                except:
                    continue
            
            if pe_ratios:
                average_pe = sum(pe_ratios) / len(pe_ratios)
            else:
                # Jika tidak ada data pembanding, gunakan P/E perusahaan sendiri
                average_pe = financial_data['info'].get('trailingPE', 15)  # Default P/E jika tidak ada data
        else:
            # Jika tidak ada perusahaan pembanding, gunakan P/E perusahaan sendiri
            average_pe = financial_data['info'].get('trailingPE', 15)  # Default P/E jika tidak ada data
        
        # Menghitung nilai saham berdasarkan P/E
        pe_value_per_share = eps * average_pe
        
        return {
            'eps': eps,
            'average_pe': average_pe,
            'pe_value_per_share': pe_value_per_share
        }
    except Exception as e:
        print(f"Error in P/E valuation: {e}")
        return None

def pbv_valuation(financial_data, target_companies=None):
    """
    Melakukan valuasi dengan metode Price to Book Value
    """
    try:
        # Mendapatkan Book Value per Share
        bvps = financial_data['info'].get('bookValue')
        if not bvps:
            # Jika tidak ada book value per share, hitung dari total equity
            balance_sheet = financial_data['balance_sheet']
            total_equity = balance_sheet.loc['Total Stockholder Equity'].iloc[-1]
            shares_outstanding = financial_data['info'].get('sharesOutstanding', 1)
            bvps = total_equity / shares_outstanding
        
        # Jika ada target perusahaan pembanding, gunakan rata-rata P/BV mereka
        if target_companies:
            pbv_ratios = []
            for ticker in target_companies:
                try:
                    company = yf.Ticker(ticker)
                    pbv_ratio = company.info.get('priceToBook')
                    if pbv_ratio and pbv_ratio > 0:
                        pbv_ratios.append(pbv_ratio)
                except:
                    continue
            
            if pbv_ratios:
                average_pbv = sum(pbv_ratios) / len(pbv_ratios)
            else:
                # Jika tidak ada data pembanding, gunakan P/BV perusahaan sendiri
                average_pbv = financial_data['info'].get('priceToBook', 2)  # Default P/BV jika tidak ada data
        else:
            # Jika tidak ada perusahaan pembanding, gunakan P/BV perusahaan sendiri
            average_pbv = financial_data['info'].get('priceToBook', 2)  # Default P/BV jika tidak ada data
        
        # Menghitung nilai saham berdasarkan P/BV
        pbv_value_per_share = bvps * average_pbv
        
        return {
            'bvps': bvps,
            'average_pbv': average_pbv,
            'pbv_value_per_share': pbv_value_per_share
        }
    except Exception as e:
        print(f"Error in P/BV valuation: {e}")
        return None

def ev_ebitda_valuation(financial_data, target_companies=None):
    """
    Melakukan valuasi dengan metode EV/EBITDA
    """
    try:
        # Menghitung EBITDA
        income_stmt = financial_data['income_stmt']
        try:
            ebit = income_stmt.loc['EBIT'].iloc[-1]
            try:
                depreciation = income_stmt.loc['Depreciation And Amortization'].iloc[-1]
            except:
                depreciation = financial_data['cash_flow'].loc['Depreciation'].iloc[-1]
            ebitda = ebit + depreciation
        except:
            # Jika tidak ada EBIT, gunakan Income Before Tax + Interest Expense
            ebitda = income_stmt.loc['Income Before Tax'].iloc[-1]
            if 'Interest Expense' in income_stmt.index:
                ebitda += abs(income_stmt.loc['Interest Expense'].iloc[-1])
        
        # Jika ada target perusahaan pembanding, gunakan rata-rata EV/EBITDA mereka
        if target_companies:
            ev_ebitda_ratios = []
            for ticker in target_companies:
                try:
                    company = yf.Ticker(ticker)
                    ev_ebitda = company.info.get('enterpriseToEbitda')
                    if ev_ebitda and ev_ebitda > 0:
                        ev_ebitda_ratios.append(ev_ebitda)
                except:
                    continue
            
            if ev_ebitda_ratios:
                average_ev_ebitda = sum(ev_ebitda_ratios) / len(ev_ebitda_ratios)
            else:
                # Jika tidak ada data pembanding, gunakan EV/EBITDA perusahaan sendiri
                average_ev_ebitda = financial_data['info'].get('enterpriseToEbitda', 10)  # Default EV/EBITDA jika tidak ada data
        else:
            # Jika tidak ada perusahaan pembanding, gunakan EV/EBITDA perusahaan sendiri
            average_ev_ebitda = financial_data['info'].get('enterpriseToEbitda', 10)  # Default EV/EBITDA jika tidak ada data
        
        # Menghitung Enterprise Value
        enterprise_value = ebitda * average_ev_ebitda
        
        # Menghitung Equity Value
        try:
            cash = financial_data['balance_sheet'].loc['Cash And Cash Equivalents'].iloc[-1]
            debt = financial_data['balance_sheet'].loc['Total Debt'].iloc[-1]
        except:
            cash = financial_data['balance_sheet'].loc['Cash And Short Term Investments'].iloc[-1] if 'Cash And Short Term Investments' in financial_data['balance_sheet'].index else 0
            debt = financial_data['balance_sheet'].loc['Long Term Debt'].iloc[-1] if 'Long Term Debt' in financial_data['balance_sheet'].index else 0
        
        equity_value = enterprise_value + cash - debt
        
        # Menghitung nilai per saham
        shares_outstanding = financial_data['info'].get('sharesOutstanding', 1)
        ev_ebitda_value_per_share = equity_value / shares_outstanding
        
        return {
            'ebitda': ebitda,
            'average_ev_ebitda': average_ev_ebitda,
            'enterprise_value': enterprise_value,
            'equity_value': equity_value,
            'ev_ebitda_value_per_share': ev_ebitda_value_per_share
        }
    except Exception as e:
        print(f"Error in EV/EBITDA valuation: {e}")
        return None

def market_multiples_valuation(ticker_symbol, target_companies):
    """
    Melakukan valuasi dengan metode Comparable Companies (Market Multiples)
    """
    try:
        # Mendapatkan data untuk perusahaan target
        target_data = get_financial_data(ticker_symbol)
        
        # Mendapatkan data untuk perusahaan pembanding
        comparable_data = {}
        for ticker in target_companies:
            data = get_financial_data(ticker)
            if data:
                comparable_data[ticker] = data
        
        # Mengumpulkan metrik valuasi dari perusahaan pembanding
        metrics = {
            'P/E': [],
            'P/BV': [],
            'EV/EBITDA': [],
            'EV/Sales': []
        }
        
        for ticker, data in comparable_data.items():
            try:
                # P/E Ratio
                pe_ratio = data['info'].get('trailingPE')
                if pe_ratio and pe_ratio > 0:
                    metrics['P/E'].append(pe_ratio)
                
                # P/BV Ratio
                pbv_ratio = data['info'].get('priceToBook')
                if pbv_ratio and pbv_ratio > 0:
                    metrics['P/BV'].append(pbv_ratio)
                
                # EV/EBITDA
                ev_ebitda = data['info'].get('enterpriseToEbitda')
                if ev_ebitda and ev_ebitda > 0:
                    metrics['EV/EBITDA'].append(ev_ebitda)
                
                # EV/Sales
                ev_sales = data['info'].get('enterpriseToRevenue')
                if ev_sales and ev_sales > 0:
                    metrics['EV/Sales'].append(ev_sales)
            except:
                continue
        
        # Menghitung rata-rata metrik
        average_metrics = {}
        for metric, values in metrics.items():
            if values:
                average_metrics[metric] = sum(values) / len(values)
        
        # Menghitung valuasi berdasarkan metrik rata-rata
        valuations = {}
        
        # P/E valuation
        if 'P/E' in average_metrics:
            try:
                eps = target_data['info'].get('trailingEPS')
                if not eps:
                    income_stmt = target_data['income_stmt']
                    net_income = income_stmt.loc['Net Income'].iloc[-1]
                    shares_outstanding = target_data['info'].get('sharesOutstanding', 1)
                    eps = net_income / shares_outstanding
                
                valuations['P/E'] = eps * average_metrics['P/E']
            except:
                pass
        
        # P/BV valuation
        if 'P/BV' in average_metrics:
            try:
                bvps = target_data['info'].get('bookValue')
                if not bvps:
                    balance_sheet = target_data['balance_sheet']
                    total_equity = balance_sheet.loc['Total Stockholder Equity'].iloc[-1]
                    shares_outstanding = target_data['info'].get('sharesOutstanding', 1)
                    bvps = total_equity / shares_outstanding
                
                valuations['P/BV'] = bvps * average_metrics['P/BV']
            except:
                pass
        
        # EV/EBITDA valuation
        if 'EV/EBITDA' in average_metrics:
            try:
                income_stmt = target_data['income_stmt']
                try:
                    ebit = income_stmt.loc['EBIT'].iloc[-1]
                    try:
                        depreciation = income_stmt.loc['Depreciation And Amortization'].iloc[-1]
                    except:
                        depreciation = target_data['cash_flow'].loc['Depreciation'].iloc[-1]
                    ebitda = ebit + depreciation
                except:
                    ebitda = income_stmt.loc['Income Before Tax'].iloc[-1]
                    if 'Interest Expense' in income_stmt.index:
                        ebitda += abs(income_stmt.loc['Interest Expense'].iloc[-1])
                
                enterprise_value = ebitda * average_metrics['EV/EBITDA']
                
                try:
                    cash = target_data['balance_sheet'].loc['Cash And Cash Equivalents'].iloc[-1]
                    debt = target_data['balance_sheet'].loc['Total Debt'].iloc[-1]
                except:
                    cash = target_data['balance_sheet'].loc['Cash And Short Term Investments'].iloc[-1] if 'Cash And Short Term Investments' in target_data['balance_sheet'].index else 0
                    debt = target_data['balance_sheet'].loc['Long Term Debt'].iloc[-1] if 'Long Term Debt' in target_data['balance_sheet'].index else 0
                
                equity_value = enterprise_value + cash - debt
                shares_outstanding = target_data['info'].get('sharesOutstanding', 1)
                
                valuations['EV/EBITDA'] = equity_value / shares_outstanding
            except:
                pass
        
        # EV/Sales valuation
        if 'EV/Sales' in average_metrics:
            try:
                revenue = target_data['income_stmt'].loc['Total Revenue'].iloc[-1]
                enterprise_value = revenue * average_metrics['EV/Sales']
                
                try:
                    cash = target_data['balance_sheet'].loc['Cash And Cash Equivalents'].iloc[-1]
                    debt = target_data['balance_sheet'].loc['Total Debt'].iloc[-1]
                except:
                    cash = target_data['balance_sheet'].loc['Cash And Short Term Investments'].iloc[-1] if 'Cash And Short Term Investments' in target_data['balance_sheet'].index else 0
                    debt = target_data['balance_sheet'].loc['Long Term Debt'].iloc[-1] if 'Long Term Debt' in target_data['balance_sheet'].index else 0
                
                equity_value = enterprise_value + cash - debt
                shares_outstanding = target_data['info'].get('sharesOutstanding', 1)
                
                valuations['EV/Sales'] = equity_value / shares_outstanding
            except:
                pass
        
        # Menghitung nilai rata-rata dari semua metrik
        if valuations:
            average_valuation = sum(valuations.values()) / len(valuations)
        else:
            average_valuation = None
        
        return {
            'average_metrics': average_metrics,
            'valuations': valuations,
            'average_valuation': average_valuation
        }
    except Exception as e:
        print(f"Error in Market Multiples valuation: {e}")
        return None

def perform_valuation(ticker_symbol, target_companies=None):
    """
    Melakukan valuasi perusahaan dengan beberapa metode
    """
    # Mendapatkan data keuangan
    financial_data = get_financial_data(ticker_symbol)
    
    if not financial_data:
        return None
    
    # Mendapatkan harga saham saat ini
    current_price = financial_data['info'].get('currentPrice')
    if not current_price:
        current_price = financial_data['hist']['Close'].iloc[-1]
    
    # Melakukan valuasi dengan berbagai metode
    valuations = {
        'ticker': ticker_symbol,
        'current_price': current_price,
        'company_name': financial_data['info'].get('longName', ticker_symbol)
    }
    
    # DCF Valuation
    dcf_result = dcf_valuation(financial_data)
    if dcf_result:
        valuations['DCF'] = dcf_result['dcf_value_per_share']
    
    # P/E Valuation
    pe_result = pe_valuation(financial_data, target_companies)
    if pe_result:
        valuations['P/E'] = pe_result['pe_value_per_share']
    
    # P/BV Valuation
    pbv_result = pbv_valuation(financial_data, target_companies)
    if pbv_result:
        valuations['P/BV'] = pbv_result['pbv_value_per_share']
    
    # EV/EBITDA Valuation
    ev_ebitda_result = ev_ebitda_valuation(financial_data, target_companies)
    if ev_ebitda_result:
        valuations['EV/EBITDA'] = ev_ebitda_result['ev_ebitda_value_per_share']
    
    # Market Multiples Valuation (jika ada perusahaan pembanding)
    if target_companies:
        mm_result = market_multiples_valuation(ticker_symbol, target_companies)
        if mm_result and mm_result['average_valuation']:
            valuations['Market Multiples'] = mm_result['average_valuation']
    
    # Menghitung nilai rata-rata dari semua metode
    valuation_methods = [v for k, v in valuations.items() if k not in ['ticker', 'current_price', 'company_name']]
    if valuation_methods:
        valuations['Average'] = sum(valuation_methods) / len(valuation_methods)
    
    return valuations

def display_valuation_results(valuations):
    """
    Menampilkan hasil valuasi dalam bentuk tabel dan grafik
    """
    if not valuations:
        print("Tidak ada hasil valuasi yang tersedia.")
        return
    
    print("\n=== HASIL VALUASI PERUSAHAAN ===")
    print(f"Ticker: {valuations['ticker']}")
    print(f"Nama Perusahaan: {valuations['company_name']}")
    print(f"Harga Saat Ini: ${valuations['current_price']:.2f}")
    print("\nMetode Valuasi:")
    
    methods = [k for k in valuations.keys() if k not in ['ticker', 'current_price', 'company_name']]
    
    for method in methods:
        value = valuations[method]
        diff = ((value / valuations['current_price']) - 1) * 100
        status = "UNDERVALUED" if diff > 0 else "OVERVALUED"
        print(f"{method}: ${value:.2f} ({diff:.2f}% {status})")
    
    # Membuat grafik perbandingan
    plt.figure(figsize=(12, 8))
    
    values = [valuations[method] for method in methods]
    colors = ['green' if v > valuations['current_price'] else 'red' for v in values]
    
    plt.bar(methods, values, color=colors)
    plt.axhline(y=valuations['current_price'], color='blue', linestyle='-', label=f'Harga Saat Ini (${valuations["current_price"]:.2f})')
    
    plt.title(f"Valuasi Perusahaan - {valuations['company_name']} ({valuations['ticker']})")
    plt.xlabel("Metode Valuasi")
    plt.ylabel("Nilai per Saham ($)")
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Menambahkan nilai di atas bar
    for i, v in enumerate(values):
        plt.text(i, v + 0.5, f"${v:.2f}", ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f"{valuations['ticker']}_valuation.png")
    plt.show()

def main():
    print("=== PROGRAM VALUASI PERUSAHAAN ===")
    ticker_symbol = input("Masukkan ticker symbol perusahaan (contoh: AAPL): ")
    
    # Opsional: menambahkan perusahaan pembanding
    use_comparable = input("Apakah ingin menggunakan perusahaan pembanding? (y/n): ").lower() == 'y'
    target_companies = None
    
    if use_comparable:
        comparable_input = input("Masukkan ticker symbol perusahaan pembanding (pisahkan dengan koma): ")
        target_companies = [ticker.strip() for ticker in comparable_input.split(',')]
    
    # Melakukan valuasi
    valuations = perform_valuation(ticker_symbol, target_companies)
    
    # Menampilkan hasil
    if valuations:
        display_valuation_results(valuations)
    else:
        print("Tidak dapat melakukan valuasi. Periksa kembali ticker symbol.")

if __name__ == "__main__":
    main()