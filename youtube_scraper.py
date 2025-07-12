from keybert import KeyBERT
import pandas as pd
from googleapiclient.discovery import build

# Initialize BERT model for keyword extraction
kw_model = KeyBERT(model='all-MiniLM-L6-v2')

API_KEY = "AIzaSyAeRc_7gXfSui2G7GmMTRsNqitSEhAiFA4"
youtube = build('youtube', 'v3', developerKey=API_KEY)

def search_youtube_videos(query, max_results=20):
    request = youtube.search().list(
        q=query,
        part='snippet',
        maxResults=max_results,
        type='video'
    )
    response = request.execute()

    results = []
    for item in response['items']:
        title = item['snippet']['title']
        keywords = extract_keywords(title)

        video_data = {
            'title': title,
            'keywords': keywords,
            'description': item['snippet']['description'],
            'publishedAt': item['snippet']['publishedAt']
        }
        results.append(video_data)

    return pd.DataFrame(results)

def extract_keywords(text):
    # Extract top keywords (phrases) using KeyBERT
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=3)
    return [kw[0] for kw in keywords]  # return just the keyword text

# Test
if __name__ == "__main__":
    df = search_youtube_videos("amazon gadgets under 500")
    print(df[['title', 'keywords']])
