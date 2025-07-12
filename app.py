import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from datetime import datetime
import subprocess
import time
from pytrends.request import TrendReq
import random
import requests
from bs4 import BeautifulSoup

# Load saved forecast results
@st.cache_data
def load_data(path="trend_results.json"):
    with open(path, "r") as f:
        data = json.load(f)
    return data

# Fetch public proxy list
@st.cache_data
def fetch_free_proxies():
    url = "https://free-proxy-list.net/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxies = []
    for row in soup.select("table tbody tr"):
        cols = row.find_all("td")
        if cols[6].text == "yes":  # Only HTTPS proxies
            proxy = f"{cols[0].text}:{cols[1].text}"
            proxies.append(proxy)
    return proxies

# Validate and return a working proxy
@st.cache_data
def get_working_proxy(timeout=3):
    reliable_proxies = [
        "159.89.132.167:3128",
        "134.209.29.120:3128",
        "51.158.68.133:8811"
    ]

    for proxy in reliable_proxies:
        try:
            response = requests.get("https://www.google.com", proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"}, timeout=timeout)
            if response.status_code == 200:
                return proxy
        except:
            continue

    proxies = fetch_free_proxies()
    random.shuffle(proxies)

    for proxy in proxies:
        try:
            response = requests.get("https://www.google.com", proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"}, timeout=timeout)
            if response.status_code == 200:
                return proxy
        except:
            continue

    return None

# Suggest related queries using pytrends with proxy
@st.cache_data
def suggest_keywords(base_keyword):
    delay = 1
    for attempt in range(3):
        try:
            proxy = get_working_proxy()
            if not proxy:
                st.sidebar.error("❌ No working proxies found.")
                return []
            pytrends = TrendReq(hl='en-US', tz=330, proxies={"https": f"http://{proxy}"})
            pytrends.build_payload([base_keyword], cat=0, timeframe='today 12-m', geo='IN')
            suggestions = pytrends.related_queries().get(base_keyword, {}).get('top', pd.DataFrame())
            if not suggestions.empty:
                return suggestions['query'].tolist()[:5]
            else:
                return []
        except Exception as e:
            st.sidebar.error(f"⚠️ Google rate limit or network issue: {e}")
            time.sleep(delay)
            delay *= 2
    return []

# Plot forecast using Plotly
def plot_forecast(forecast_data, keyword, start_date=None, end_date=None):
    df = pd.DataFrame(forecast_data)
    df["ds"] = pd.to_datetime(df["ds"])

    if start_date:
        df = df[df["ds"] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df["ds"] <= pd.to_datetime(end_date)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["ds"], y=df["yhat"], mode="lines", name=keyword))
    fig.update_layout(title=f"📈 Forecast for '{keyword}'", xaxis_title="Date", yaxis_title="Trend")
    return fig

# Streamlit UI
st.set_page_config(page_title="Trend Forecast Dashboard", layout="wide")
st.title("📊 Google Trends Forecast Dashboard")

# Run Pipeline Button
run_clicked = st.sidebar.button("🔁 Run Trend Pipeline")
if run_clicked:
    with st.spinner("Running pipeline..."):
        result = subprocess.run(["python", "trend_pipeline.py"], capture_output=True, text=True)
        if result.returncode == 0:
            st.sidebar.success("✅ Pipeline completed successfully!")
        else:
            st.sidebar.error(f"❌ Pipeline failed: {result.stderr}")

# Load existing forecast data
data = load_data()

# Keyword Suggestion
st.sidebar.subheader("🔍 Keyword Suggestions")
base_keyword = st.sidebar.text_input("Enter base keyword")
if base_keyword:
    suggestions = suggest_keywords(base_keyword)
    if suggestions:
        st.sidebar.write("💡 Suggested Keywords:")
        selected_suggestions = st.sidebar.multiselect("Select to analyze", suggestions)

        if selected_suggestions:
            with open("trending_keywords.csv", "a") as f:
                for kw in selected_suggestions:
                    f.write(f"{kw}\n")
            st.sidebar.success("✅ Keywords added to pipeline input. Click 'Run Trend Pipeline' to fetch new forecasts.")
    else:
        st.sidebar.warning("No suggestions found or network issue.")

# Sidebar Keyword Selection
all_keywords = [item["Keyword"] for item in data]
selected_keywords = st.sidebar.multiselect("Select one or more keywords", all_keywords, default=all_keywords[:1])

# Sidebar Date Filter
start_date = st.sidebar.date_input("Start Date", None)
end_date = st.sidebar.date_input("End Date", None)

# Display comparison chart
if selected_keywords:
    fig = go.Figure()
    for keyword in selected_keywords:
        selected_data = next(item for item in data if item["Keyword"] == keyword)
        df = pd.DataFrame(selected_data["Forecast"])
        df["ds"] = pd.to_datetime(df["ds"])

        if start_date:
            df = df[df["ds"] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df["ds"] <= pd.to_datetime(end_date)]

        fig.add_trace(go.Scatter(x=df["ds"], y=df["yhat"], mode="lines", name=keyword))

    fig.update_layout(title="📈 Forecast Comparison", xaxis_title="Date", yaxis_title="Trend")
    st.plotly_chart(fig, use_container_width=True)

    # Show trend scores
    scores = {item["Keyword"]: item["Score"] for item in data if item["Keyword"] in selected_keywords}
    st.subheader("🔥 Trend Scores")
    st.dataframe(pd.DataFrame(list(scores.items()), columns=["Keyword", "Score"]))
else:
    st.warning("⚠️ Please select at least one keyword.")
