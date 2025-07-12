# 📊 Google Trends Forecast Dashboard

A Streamlit-based web app that visualizes Google Trends forecast data for selected keywords using Prophet. It helps you track trending products, monitor market interest, and make data-informed decisions using real-time and forecasted data.

---

## 🚀 Features

- 🔍 **Keyword Suggestions** (via Google Trends Related Queries)
- 📈 **7-Day Forecast** for each keyword using Facebook Prophet
- 📊 **Multi-keyword Comparison Charts** with date filtering
- 📥 **CSV Export** of raw forecast data
- ✅ **Run Trend Pipeline from Streamlit**
- 🧠 **Trend Scoring** via real-time Google Trends data
- 🌐 **Proxy Support** to bypass Google rate-limits (Error 429)

---
##YouTube Trend Scraper:
-Scrape video titles, views, upload dates, and descriptions for a given keyword
-Extract the top trending videos relevant to your keywords
-Optionally, compute a “YouTube Score” (views × recency × keyword match) to supplement the Google Trends Score
## 🛠 Tech Stack

- **Python 3.10**
- **Streamlit** – Web UI
- **Facebook Prophet** – Time series forecasting
- **PyTrends** – Google Trends API wrapper
- **Plotly** – Interactive visualizations
- **aiohttp** – Async parallel requests with exponential backoff
- **subprocess** – For pipeline execution
- **pandas**, **json**, **datetime** – Data handling

---

## 🔧 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/MayankSinghRaghav/trend_predictor.git
cd trend_predictor
