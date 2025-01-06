# Reddit Scraper

<div align="center">

![Reddit Logo](https://img.shields.io/badge/Reddit-FF4500?style=for-the-badge&logo=reddit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

[![Python Versions](https://img.shields.io/pypi/pyversions/streamlit.svg)](https://pypi.org/project/streamlit/)

A powerful Reddit scraper with data visualization and sentiment analysis capabilities.

</div>

## Features

### Subreddit Posts Scraper
- 📊 Analytics Dashboard with score vs. comments distribution
- 🔤 Word Cloud generation from post titles
- 😊 Sentiment Analysis of posts
- 📑 Raw data access and CSV export
- 🔍 Interactive Post Explorer

### Specific Post URL Scraper
- 📝 Detailed post information
- 💭 Comment analysis and sorting
- 📊 Comment statistics and visualizations
- 😊 Sentiment analysis of comments
- 🔤 Word Cloud generation from comments

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/NotIshi28/reddit-scraper.git
   cd reddit-scraper
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Get your secrets from reddit api creds from: https://www.reddit.com/prefs/apps

## Requirements
```txt
praw==7.7.1
pandas==2.0.3
streamlit==1.24.1
plotly==5.15.0
altair==5.0.1
textblob==0.17.1
wordcloud==1.9.2
matplotlib==3.7.2
python-dotenv==1.0.0
```

## Usage

1. Run the Streamlit app:
   ```bash
   streamlit run main.py
   ```

2. Choose scraping option:
   - Subreddit Posts: Enter subreddit name and customize scraping parameters
   - Specific Post URL: Enter a Reddit post URL to analyze its comments

3. Explore the data through various tabs:
   - Analytics Dashboard
   - Word Cloud Visualization
   - Sentiment Analysis
   - Raw Data
   - Post/Comment Explorer

## Features in Detail

### Analytics
- Score vs. Comments Distribution
- Top Posts by Score
- Comment Score Distribution
- Top Commenters Analysis

### Sentiment Analysis
- Sentiment Distribution Visualization
- Positive/Neutral/Negative Classification
- Sentiment Filtering
- Detailed Sentiment Metrics

### Data Export
- Download Post Data as CSV
- Download Comments as CSV
- Sorted and Filtered Data Export

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool is for educational purposes only. Please respect Reddit's API terms of service and rate limits when using this scraper.

---

<div align="center">
Made with ❤️ by NotIshi28
</div>