import requests
import pandas as pd
import time
from datetime import datetime

# 1. Fetch market data (with rate-limit retry)
def fetch_market_data(vs_currency="usd", per_page=250, page=1, retries=3):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": page,
        "sparkline": False,
        # CRITICAL FIX: Request 7d data explicitly
        "price_change_percentage": "24h,7d"  # Must specify timeframes
    }

    headers = {
        "Accept": "application/json",
        "User-Agent": "TopMoversBot/1.0"
    }

    for attempt in range(retries):
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            time.sleep(1.25)  # respect rate limit
            return response.json()

        elif response.status_code == 429:
            wait_time = 10 * (attempt + 1)
            print(f"⚠️ Rate limited (429). Retrying in {wait_time}s...")
            time.sleep(wait_time)

        else:
            print(f"❌ Request failed with {response.status_code}: {response.text}")
            break

    raise Exception("❌ Failed after retries due to rate limiting.")

# 2. Process and label gainers & losers (using 7d data)
def get_combined_movers(data, top_n=20):
    df = pd.DataFrame(data)
    
    # CORRECT FIELD NAMES - Verified with CoinGecko API
    required_columns = [
        "id", 
        "symbol", 
        "name", 
        "current_price",
        "price_change_percentage_24h",
        "price_change_percentage_7d"  # CORRECT 7D FIELD NAME
    ]
    
    # Filter out coins missing 7d data
    df = df.dropna(subset=["price_change_percentage_7d"])
    df = df[required_columns]
    
    # Rename for readability
    df = df.rename(columns={
        "price_change_percentage_24h": "24h_change_%",
        "price_change_percentage_7d": "7d_change_%"
    })

    # Sort by 7-day performance
    gainers = df.sort_values(by="7d_change_%", ascending=False).head(top_n)
    gainers["type"] = "gainer_7d"

    losers = df.sort_values(by="7d_change_%", ascending=True).head(top_n)
    losers["type"] = "loser_7d"

    combined = pd.concat([gainers, losers], ignore_index=True)
    return combined

# 3. Save to CSV
def save_to_csv(df, filename):
    df.to_csv(filename, index=False)
    print(f"✅ Combined movers saved to {filename}")
    print(f"📊 Top 3 7d Gainers:\n{gainers.head(3)[['name', '7d_change_%']]}")
    print(f"📉 Top 3 7d Losers:\n{losers.head(3)[['name', '7d_change_%']]}")

# 4. Main execution
if __name__ == "__main__":
    try:
        print("📡 Fetching CoinGecko market data (including 7d performance)...")
        data = fetch_market_data()

        print(f"📦 Retrieved {len(data)} coins. Processing 7-day movers...")
        movers = get_combined_movers(data)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"TopGainersAndLosers_7d_{timestamp}.csv"

        save_to_csv(movers, filename)

    except Exception as e:
        print(f"❌ Critical Error: {str(e)}")
        print("💡 Try these fixes:")
        print("1. Check internet connection")
        print("2. Verify CoinGecko API status: https://status.coingecko.com")
        print("3. Reduce 'per_page' parameter if rate-limited")
