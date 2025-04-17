import requests
import csv
from datetime import datetime

def fetch_kline_data(symbol="ETHUSDT", interval="1h", limit=24):
    url = "https://api.mexc.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        klines = response.json()

        if not klines:
            print("⚠️ No data returned.")
            return []

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

        filename = f"{symbol}_{interval}_klines.csv"
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=formatted[0].keys())
            writer.writeheader()
            writer.writerows(formatted)

        print(f"✅ Saved {len(formatted)} candles to {filename}")
        return formatted

    except requests.exceptions.HTTPError as err:
        print(f"❌ HTTP error: {err}")
        print(f"❗ Response content: {response.text}")
    except Exception as e:
        print(f"❌ General error: {e}")

    return []

# Example call
if __name__ == "__main__":
    fetch_kline_data("ETHUSDT", "1h", 24)
