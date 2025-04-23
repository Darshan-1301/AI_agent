# This script fetches finance and geopolitics news from RSS feeds, summarizes the articles,
# and retrieves real-time stock prices for Indian stocks using web scraping.
import feedparser
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import streamlit as st

# RSS feeds for finance and geopolitics news
RSS_FEEDS = {
    "finance": [
        "https://www.financialexpress.com/feed/",
        "https://www.moneycontrol.com/rss/MCtopnews.xml"
    ],
    "geopolitics": [
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
    ]
}

def fetch_news():
    articles = []
    for category, feeds in RSS_FEEDS.items():
        for url in feeds:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:  # limit to 5 recent articles per feed
                articles.append({
                    "title": entry.title,
                    "summary": entry.get("summary", ""),
                    "link": entry.link,
                    "category": category
                })
    return articles

def fetch_stock_price(stock_symbol):
    url = f"https://www.google.com/finance/quote/{stock_symbol}:NSE"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    price_span = soup.find("div", class_="YMlKec fxKbKc")
    if price_span:
        return price_span.text.strip()
    return "N/A"

# Load summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text):
    max_chunk = 500
    text = text.replace("\n", " ")
    if len(text) > max_chunk:
        text = text[:max_chunk]
    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
    return summary[0]['summary_text']

# Streamlit app UI
st.title("Finance & Geopolitics News + Indian Stocks Summary")

with st.spinner("Fetching news..."):
    articles = fetch_news()

st.header("News Summaries")
for article in articles[:10]:  # show top 10 articles
    st.subheader(f"{article['title']} ({article['category']})")
    summary = summarize_text(article['summary'] or article['title'])
    st.write(summary)
    st.markdown(f"[Read more]({article['link']})")

st.header("Real-time Indian Stock Prices")
stocks = ["INFY", "TCS", "RELIANCE", "HDFCBANK", "ICICIBANK"]
for symbol in stocks:
    price = fetch_stock_price(symbol)
    st.write(f"**{symbol}**: {price}")
