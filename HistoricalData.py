import requests
import csv
from datetime import datetime

def fetch_kline_data(symbol="ETHUSDT", interval="1h", limit=24):
    url = "https://api.mexc.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit  # Max 1000
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    klines = response.json()

    # Format: [time, open, high, low, close, volume, ...]
    formatted = [
        {
            "Time": datetime.fromtimestamp(k[0] // 1000).strftime('%Y-%m-%d %H:%M'),
            "Open": k[1],
            "High": k[2],
            "Low": k[3],
            "Close": k[4],
            "Volume": k[5]
        } for k in klines
    ]

    # Optional: save to CSV
    filename = f"{symbol}_{interval}_klines.csv"
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=formatted[0].keys())
        writer.writeheader()
        writer.writerows(formatted)

    print(f"✅ Saved {len(formatted)} candles to {filename}")
    return formatted

# Example usage
if __name__ == "__main__":
    data = fetch_kline_data("ETHUSDT", "1h", limit=24)
    for row in data[:5]:  # preview first 5 rows
        print(row)
