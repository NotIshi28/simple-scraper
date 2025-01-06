import praw
import pandas as pd
import os
import time
from dotenv import load_dotenv
import streamlit as st
import plotly.express as px
import altair as alt
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

if os.path.exists('.env'):
    load_dotenv()

def init_reddit():

    client_id = os.environ.get("REDDIT_CLIENT_ID") or st.secrets["REDDIT_CLIENT_ID"]
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET") or st.secrets["REDDIT_CLIENT_SECRET"]
    user_agent = os.environ.get("REDDIT_USER_AGENT") or st.secrets["REDDIT_USER_AGENT"]
    
    return praw.Reddit(
        client_id=client_id,         
        client_secret=client_secret,      
        user_agent=user_agent,
        check_for_async=False
    )

@st.cache_data(ttl=3600)

def get_subreddit_posts(_reddit, subreddit_name, post_limit, time_filter="month"):
    try:
        subreddit = _reddit.subreddit(subreddit_name)
        posts_dict = {
            "Title": [], 
            "Post Text": [],
            "ID": [], 
            "Score": [],
            "Total Comments": [], 
            "Post URL": []
        }
        
        for post in subreddit.top(limit=post_limit, time_filter=time_filter):
            posts_dict["Title"].append(post.title)
            posts_dict["Post Text"].append(post.selftext)
            posts_dict["ID"].append(post.id)
            posts_dict["Score"].append(post.score)
            posts_dict["Total Comments"].append(post.num_comments)
            posts_dict["Post URL"].append(post.url)
        
        return pd.DataFrame(posts_dict)
    except Exception as e:
        st.error(f"Error fetching subreddit posts: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)

def get_post_by_url(_reddit, url):
    try:
        submission = _reddit.submission(url=url)
        
        post_data = {
            "Title": submission.title,
            "Post Text": submission.selftext,
            "ID": submission.id,
            "Score": submission.score,
            "Total Comments": submission.num_comments,
            "Post URL": submission.url
        }
        
        post_comments = []
        submission.comments.replace_more(limit=None)
        
        for comment in submission.comments.list():
            comment_data = {
                "Comment Text": comment.body,
                "Score": comment.score,
                "Author": str(comment.author),
                "Created UTC": comment.created_utc
            }
            post_comments.append(comment_data)
        
        return pd.DataFrame([post_data]), pd.DataFrame(post_comments)
    except Exception as e:
        st.error(f"Error fetching post: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()  

def show_analytics(df):
    if len(df) < 2:
        st.warning("Not enough data for analysis. Please try scraping more posts.")
        return
    st.subheader("📊 Analytics Dashboard")
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.scatter(df, x='Score', y='Total Comments',
                        hover_data=['Title'], 
                        title='Score vs Comments Distribution')
        st.plotly_chart(fig)
    
    with col2:
        chart = alt.Chart(df.head(10)).mark_bar().encode(
            x='Score',
            y=alt.Y('Title', sort='-x'),
            tooltip=['Title', 'Score', 'Total Comments']
        ).properties(title='Top 10 Posts by Score')
        st.altair_chart(chart, use_container_width=True)


def preprocess_text(text):
    """Basic text preprocessing"""
    
    text = text.lower()
    
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    text = ' '.join(text.split())
    return text

def generate_custom_wordcloud(df, width=800, height=400, background_color='white'):
    """Generate a custom word cloud with more options"""
    
    text = ' '.join(df['Title'].apply(preprocess_text))
    
    wordcloud = WordCloud(
        width=width,
        height=height,
        background_color=background_color,
        max_words=200,
        colormap='viridis',
        contour_width=3,
        contour_color='steelblue'
    ).generate(text)
    
    return wordcloud

def detailed_sentiment_analysis(text):
    """Perform detailed sentiment analysis"""
    analysis = TextBlob(text)
    return {
        'polarity': analysis.sentiment.polarity,
        'subjectivity': analysis.sentiment.subjectivity,
        'label': 'Positive 😊' if analysis.sentiment.polarity > 0 
                else ('Negative ☹️' if analysis.sentiment.polarity < 0 
                else 'Neutral 😐')
    }

def main():
    st.snow()

    st.title("Simple Scraper")
    
    reddit = init_reddit()
    
    st.sidebar.header("Settings")
    scrape_option = st.sidebar.radio(
        "Choose scraping option:",
        ["Subreddit Posts", "Specific Post by URL"]
    )
    
    if scrape_option == "Subreddit Posts":
        st.header("Subreddit Posts Scraper")
        
        subreddit_name = st.text_input("Enter subreddit name:", "funny")
        post_limit = st.slider("Number of posts to scrape:", 1, 100, 5)
        time_filter = st.selectbox(
            "Time filter:",
            ["day", "week", "month", "year", "all"]
        )
        
        if st.button("Scrape Subreddit"):
            with st.spinner("Scraping posts..."):
                try:
                    df = get_subreddit_posts(reddit, subreddit_name, post_limit, time_filter)
                    if not df.empty:
                        st.success(f"Successfully scraped {len(df)} posts!")
                        
                        tab1, tab2, tab3, tab4, tab5 = st.tabs([
                            "📊 Analytics",
                            "🔤 Word Cloud",
                            "😊 Sentiment",
                            "📑 Raw Data",
                            "🔍 Post Explorer"
                        ])
                        
                        with tab1:
                            show_analytics(df)
                        
                        with tab2:
                            with st.spinner("Generating word cloud..."):
                                try:
                                    generate_custom_wordcloud(df)
                                except Exception as e:
                                    st.error(f"Error generating word cloud: {str(e)}")
                            
                            width = 800
                            height = 400
                            background_color = "#FFFFFF"
                            
                            text = ' '.join(df['Title'].astype(str))
                            wordcloud = WordCloud(
                                width=width,
                                height=height,
                                background_color=background_color
                            ).generate(text)
                            
                            fig, ax = plt.subplots()
                            ax.imshow(wordcloud, interpolation='bilinear')
                            ax.axis('off')
                            st.pyplot(fig)
                        
                        with tab3:                        
                            st.subheader("Sentiment Analysis")
                            
                            df['Sentiment'] = df['Title'].apply(lambda x: TextBlob(x).sentiment.polarity)
                            df['Sentiment_Label'] = df['Sentiment'].apply(
                                lambda x: "Positive 😊" if x > 0 else ("Negative ☹️" if x < 0 else "Neutral 😐")
                            )
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                positive_count = len(df[df['Sentiment'] > 0])
                                st.metric("Positive Posts 😊", positive_count)
                            with col2:
                                neutral_count = len(df[df['Sentiment'] == 0])
                                st.metric("Neutral Posts 😐", neutral_count)
                            with col3:
                                negative_count = len(df[df['Sentiment'] < 0])
                                st.metric("Negative Posts ☹️", negative_count)
                            
                            fig = px.histogram(
                                df, 
                                x='Sentiment',
                                title='Sentiment Distribution of Post Titles',
                                labels={'Sentiment': 'Sentiment Score (-1 to 1)'},
                                color='Sentiment_Label'
                            )
                            st.plotly_chart(fig)
                            
                            sentiment_filter = st.selectbox(
                                "Filter posts by sentiment:",
                                ["All", "Positive 😊", "Neutral 😐", "Negative ☹️"]
                            )
                            
                            if sentiment_filter != "All":
                                filtered_df = df[df['Sentiment_Label'] == sentiment_filter]
                            else:
                                filtered_df = df
                                
                            st.write(filtered_df[['Title', 'Sentiment', 'Score', 'Total Comments']])
                        
                        with tab4:
                            st.dataframe(df)
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                "Download CSV",
                                csv,
                                f"{subreddit_name}_posts.csv",
                                "text/csv",
                                key='download-csv'
                            )
                        
                        with tab5:
                            st.subheader("Explore Posts")
                            selected_post = st.selectbox(
                                "Select a post to view details:",
                                df['Title'].tolist()
                            )
                            if selected_post:
                                post_data = df[df['Title'] == selected_post].iloc[0]
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("Score", post_data['Score'])
                                    st.metric("Comments", post_data['Total Comments'])
                                with col2:
                                    sentiment = TextBlob(post_data['Title']).sentiment.polarity
                                    st.metric("Sentiment", f"{sentiment:.2f}")
                                
                                st.write("**Post Text:**")
                                st.write(post_data['Post Text'])
                                st.markdown(f"[View on Reddit]({post_data['Post URL']})")
                                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    else:
        st.header("Post URL Scraper")
        
        post_url = st.text_input("Enter Reddit post URL:")
        
        if st.button("Scrape Post"):
            with st.spinner("Scraping post and comments..."):
                try:
                    post_df, comments_df = get_post_by_url(reddit, post_url)
                    
                    if not post_df.empty and not comments_df.empty:
                        st.success(f"Successfully scraped post and {len(comments_df)} comments!")
                        
                        tab1, tab2, tab3, tab4, tab5 = st.tabs([
                            "📝 Post Details",
                            "💭 Comments",
                            "📊 Analytics",
                            "😊 Sentiment Analysis",
                            "🔤 Word Cloud"
                        ])
                        
                        with tab1:
                            st.subheader("Post Details")
                            st.dataframe(post_df)
                            post_csv = post_df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                "Download Post CSV",
                                post_csv,
                                "post_details.csv",
                                "text/csv",
                                key='download-post'
                            )
                        
                        with tab2:
                            st.subheader(f"Comments ({len(comments_df)} total)")
                            
                            
                            sort_by = st.selectbox(
                                "Sort comments by:",
                                ["Score", "Created UTC", "Author"]
                            )
                            sort_order = st.radio("Sort order:", ["Descending", "Ascending"])
                            
                            
                            ascending = sort_order == "Ascending"
                            sorted_comments = comments_df.sort_values(by=sort_by, ascending=ascending)
                            
                            st.dataframe(sorted_comments)
                            comments_csv = sorted_comments.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                "Download Comments CSV",
                                comments_csv,
                                "comments.csv",
                                "text/csv",
                                key='download-comments'
                            )
                        
                        with tab3:
                            st.subheader("Comments Analytics")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Comments", len(comments_df))
                            with col2:
                                st.metric("Average Score", f"{comments_df['Score'].mean():.1f}")
                            with col3:
                                st.metric("Unique Authors", len(comments_df['Author'].unique()))
                            
                            
                            fig = px.histogram(
                                comments_df,
                                x='Score',
                                title='Comment Score Distribution',
                                labels={'Score': 'Comment Score'}
                            )
                            st.plotly_chart(fig)
                            
                            
                            st.subheader("Top Commenters")
                            
                            author_stats = comments_df['Author'].value_counts().head(10)
                            
                            fig = px.bar(
                                x=author_stats.index,
                                y=author_stats.values,
                                title='Top 10 Commenters',
                                labels={'x': 'Author', 'y': 'Number of Comments'}
                            )
                            st.plotly_chart(fig)
                        
                        with tab4:
                            st.subheader("Sentiment Analysis")
                            
                            comments_df['Sentiment'] = comments_df['Comment Text'].apply(
                                lambda x: TextBlob(str(x)).sentiment.polarity
                            )
                            comments_df['Sentiment_Label'] = comments_df['Sentiment'].apply(
                                lambda x: "Positive 😊" if x > 0 else ("Negative ☹️" if x < 0 else "Neutral 😐")
                            )
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                positive_count = len(comments_df[comments_df['Sentiment'] > 0])
                                st.metric("Positive Comments 😊", positive_count)
                            with col2:
                                neutral_count = len(comments_df[comments_df['Sentiment'] == 0])
                                st.metric("Neutral Comments 😐", neutral_count)
                            with col3:
                                negative_count = len(comments_df[comments_df['Sentiment'] < 0])
                                st.metric("Negative Comments ☹️", negative_count)
                            
                            fig = px.histogram(
                                comments_df,
                                x='Sentiment',
                                color='Sentiment_Label',
                                title='Comment Sentiment Distribution',
                                labels={'Sentiment': 'Sentiment Score (-1 to 1)'}
                            )
                            st.plotly_chart(fig)
                            
                            sentiment_filter = st.selectbox(
                                "Filter comments by sentiment:",
                                ["All", "Positive 😊", "Neutral 😐", "Negative ☹️"]
                            )
                            
                            if sentiment_filter != "All":
                                filtered_df = comments_df[comments_df['Sentiment_Label'] == sentiment_filter]
                            else:
                                filtered_df = comments_df
                                
                            st.dataframe(filtered_df[['Comment Text', 'Sentiment', 'Score', 'Author']])
                        
                        with tab5:
                            st.subheader("Word Cloud from Comments")
                            
                            
                            all_comments_text = ' '.join(comments_df['Comment Text'].astype(str))
                            
                            width = 800
                            height = 400
                            background_color = "#FFFFFF"                  
                            
                            wordcloud = WordCloud(
                                width=width,
                                height=height,
                                background_color=background_color,
                                max_words=200,
                                colormap='viridis',
                                contour_width=3,
                                contour_color='steelblue'
                            ).generate(preprocess_text(all_comments_text))
                            
                            fig, ax = plt.subplots()
                            ax.imshow(wordcloud, interpolation='bilinear')
                            ax.axis('off')
                            st.pyplot(fig)
                    
                    else:
                        st.warning("No data found for this URL. Please check if the URL is correct.")
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()