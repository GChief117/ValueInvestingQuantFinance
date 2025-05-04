import yfinance as yf
import pandas as pd
from datetime import datetime
from tqdm import tqdm  

#Output for Cigar Butt
def evaluate_cigar_butt(ticker_symbol, print_report=False):
    stock = yf.Ticker(ticker_symbol)

    price_history = stock.history(period='1d')
    if price_history.empty:
        return None
    price = price_history['Close'].iloc[-1]

    balance_sheet = stock.balance_sheet
    try:
        current_assets = balance_sheet.loc['Current Assets'].iloc[0]
        total_liabilities = balance_sheet.loc['Total Liabilities Net Minority Interest'].iloc[0]
    except KeyError:
        return None

    info = stock.info
    market_cap = info.get('marketCap', None)
    if market_cap is None:
        return None
    shares_outstanding = market_cap / price

    ncav = current_assets - total_liabilities
    ncav_per_share = ncav / shares_outstanding
    is_cigar_butt = price < ncav_per_share

    if is_cigar_butt and print_report:
        print(f"\n📊 --- {ticker_symbol.upper()} Balance Sheet Snapshot ---")
        balance_display = balance_sheet.copy()
        balance_display.columns = [str(date.date()) for date in balance_display.columns]
        print(balance_display.fillna("—").astype(str).head(20))

        print(f"\n📌 --- {ticker_symbol.upper()} Cigar Butt Evaluation ---")
        print(f"🟡 Market Price:         ${price:,.2f}")
        print(f"🟢 Current Assets:       ${current_assets:,.0f}")
        print(f"🔴 Total Liabilities:    ${total_liabilities:,.0f}")
        print(f"🧮 Shares Outstanding:   {shares_outstanding:,.0f}")
        print(f"📘 NCAV per Share:       ${ncav_per_share:.2f}")
        print(f"📉 BUY Signal (Price < NCAV)? → ✅ YES — Cigar Butt!")

    if is_cigar_butt:
        return {
            "Ticker": ticker_symbol,
            "Price": round(price, 2),
            "Current Assets": round(current_assets),
            "Total Liabilities": round(total_liabilities),
            "Shares Outstanding": round(shares_outstanding),
            "NCAV per Share": round(ncav_per_share, 2),
            "BUY Signal": "✅ YES"
        }

    return None

# Scanning for Cigar Butts and Progress bar
def scan_cigar_butts(csv_path, output_path="cigar_butts_found.csv", limit=100):
    df = pd.read_csv(csv_path)
    tickers = df['Symbol'].dropna().tolist()

    cigar_butts = []

    print(f"\n🔍 Scanning up to {limit} tickers from {csv_path}...\n")

    #Progress bar
    for ticker in tqdm(tickers[:limit], desc="🔎 Progress", unit="stock"):
        try:
            result = evaluate_cigar_butt(ticker, print_report=True)
            if result:
                result["Date"] = datetime.today().strftime("%Y-%m-%d")
                cigar_butts.append(result)
        except Exception as e:
            tqdm.write(f"⚠️ Error on {ticker}: {e}")
            continue

    if cigar_butts:
        output_df = pd.DataFrame(cigar_butts)
        output_df.to_csv(output_path, index=False)
        print(f"\n✅ Saved {len(cigar_butts)} cigar butt stocks to {output_path}")
    else:
        print("\n❌ No cigar butt stocks found.")

# Run
scan_cigar_butts("path to.../symbols.csv", limit=6834)
