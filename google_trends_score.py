from pytrends.request import TrendReq
from prophet import Prophet
import logging
import pandas as pd

# Logging Setup
logging.basicConfig(
    filename='trend_predictor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ✅ Simple Pytrends Initialization — no custom session
pytrends = TrendReq(
    hl='en-US',
    tz=330,
    timeout=(10, 25)
)

# ----------------- Get Trend Score ----------------- #
def get_trend_score(keyword, timeframe='today 12-m'):
    logging.info(f"Fetching trend score for keyword: {keyword}")
    try:
        pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo='IN')
        data = pytrends.interest_over_time()

        if data.empty:
            logging.warning(f"No trend data returned for: {keyword}")
            return 0

        score = round(data[keyword].mean(), 2)
        logging.info(f"Trend score for '{keyword}': {score}")
        return score

    except Exception as e:
        logging.error(f"Error fetching trend score for '{keyword}': {e}")
        print(f"❌ Error getting score for '{keyword}': {e}")
        return 0

# ----------------- Forecast with Prophet ----------------- #
def forecast_trend(keyword, days=7, show_plot=False):
    try:
        logging.info(f"Forecasting trend for keyword: {keyword}")

        pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='IN')
        df = pytrends.interest_over_time()

        if df.empty:
            logging.warning(f"Google Trends returned empty data for '{keyword}'")
            print(f"⚠️ Google Trends returned empty data for '{keyword}'")
            return None

        if 'isPartial' in df.columns:
            df = df[~df['isPartial']]

        if len(df) < 10:
            logging.warning(f"Not enough data to forecast for '{keyword}'")
            print(f"⚠️ Not enough data to forecast for '{keyword}'")
            return None

        # Prepare for Prophet
        data = df.reset_index()[['date', keyword]]
        data.columns = ['ds', 'y']

        if data['y'].sum() == 0:
            logging.warning(f"All trend values are zero for '{keyword}'")
            print(f"⚠️ All trend values are zero for '{keyword}'")
            return None

        model = Prophet()
        model.fit(data)

        future = model.make_future_dataframe(periods=days)
        forecast = model.predict(future)

        if show_plot:
            import matplotlib.pyplot as plt
            model.plot(forecast)
            plt.title(f"Forecast for {keyword}")
            plt.show()

        logging.info(f"Forecast complete for '{keyword}'")
        return forecast[['ds', 'yhat']]

    except Exception as e:
        logging.error(f"Error forecasting trend for '{keyword}': {e}")
        print(f"❌ Error forecasting trend for '{keyword}': {e}")
        return None
