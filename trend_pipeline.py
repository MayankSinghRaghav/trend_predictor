import pandas as pd
import json
import time
import os
from datetime import datetime
import random
import warnings
import asyncio
import aiohttp
from google_trends_score import get_trend_score, forecast_trend

warnings.filterwarnings("ignore", category=FutureWarning)

# 📥 Load keywords from CSV file
def load_keywords(file_path="trending_keywords.csv"):
    df = pd.read_csv(file_path)
    return df["Keyword"].dropna().tolist()

# 🔁 Async version to process each keyword with backoff and retry
async def process_keyword(keyword, save_raw=False):
    print(f"\n🔍 Processing: {keyword}")
    retry_delay = 60

    for attempt in range(5):
        try:
            score = get_trend_score(keyword)
            forecast = forecast_trend(keyword, days=7, show_plot=False)

            if forecast is None or len(forecast) == 0:
                print(f"⚠️ Skipping '{keyword}' — no usable forecast data.")
                return None

            if save_raw:
                raw_dir = "raw_trends"
                os.makedirs(raw_dir, exist_ok=True)
                forecast.to_csv(
                    os.path.join(raw_dir, f"{keyword.replace(' ', '_')}_forecast.csv"), 
                    index=False
                )

            await asyncio.sleep(random.randint(30, 90))

            return {
                "Keyword": keyword,
                "Score": score,
                "Forecast": forecast[['ds', 'yhat']].to_dict(orient='records')
            }

        except Exception as e:
            print(f"❌ Error: {e}")
            print(f"⏳ Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)
            retry_delay *= 2

    return None

# 💾 Save results to JSON
def convert_timestamps(obj):
    if isinstance(obj, dict):
        return {k: convert_timestamps(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_timestamps(i) for i in obj]
    elif isinstance(obj, (pd.Timestamp, datetime)):
        return str(obj)
    return obj

def save_results(data, filename="trend_results.json"):
    cleaned_data = convert_timestamps(data)
    with open(filename, "w") as f:
        json.dump(cleaned_data, f, indent=2)

# 🚀 Main function
async def main():
    keywords = load_keywords()
    print(f"📥 Loaded {len(keywords)} keywords")

    tasks = [process_keyword(k, save_raw=True) for k in keywords]
    raw_results = await asyncio.gather(*tasks)
    data = [r for r in raw_results if r]

    if not data:
        print("⚠️ No valid trend data found. Please try different or broader keywords.")
    else:
        print(f"\n✅ Processed {len(data)} keywords with valid trend forecasts.")
        save_results(data)
        print("📁 Results saved to 'trend_results.json'")

if __name__ == "__main__":
    asyncio.run(main())
