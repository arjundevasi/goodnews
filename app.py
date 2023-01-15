
from cs50 import SQL

from flask import Flask,render_template,redirect

import feedparser
import boto3
app = Flask(__name__)

db = SQL("sqlite:///news.db")

@app.route("/")
def home():
    ## query database for positive only news
    pos_articles = db.execute("SELECT * FROM news WHERE sentiment = ? ORDER BY id DESC","POSITIVE")
    rows_p = len(pos_articles)
    ## create a 2d list
    news_p = [[0 for i in range(4)] for j in range(rows_p)]
    
    # saving data in a list
    for i in range(len(pos_articles)):
        title = pos_articles[i]['title']
        link = pos_articles[i]['link']
        publisher = pos_articles[i]['publisher']
        date = pos_articles[i]['date']

        news_p[i][0] = title
        news_p[i][1] = link
        news_p[i][2] = publisher
        news_p[i][3] = date
        
    
    ## query database for neutral
    neu_articles = db.execute("SELECT * FROM news WHERE score > ? ORDER BY id DESC",90)
    rows_n = len(neu_articles)
    ## create a 2d list
    news_n = [[0 for i in range(4)] for j in range(rows_n)]
    
    # saving data in a list
    for i in range(len(neu_articles)):
        title = neu_articles[i]['title']
        link = neu_articles[i]['link']
        publisher = neu_articles[i]['publisher']
        date = neu_articles[i]['date']

        news_n[i][0] = title
        news_n[i][1] = link
        news_n[i][2] = publisher
        news_n[i][3] = date
    
    ## extend or merge both list
    news_p.extend(news_n)
    rows = len(news_p)
    return render_template("index.html",news=news_p,len=rows)

@app.route("/generate")
def generate():
    agencies = ["https://rss.nytimes.com/services/xml/rss/nyt/World.xml","https://feeds.a.dj.com/rss/RSSWorldNews.xml",
                "https://news.google.com/rss","http://feeds.bbci.co.uk/news/world/rss.xml#",
                "https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best",
                "http://rss.cnn.com/rss/edition.rss","https://news.yahoo.com/rss/world",
                "https://www.indiatoday.in/rss/1206577","https://www.thehindu.com/news/international/feeder/default.rss",
                "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms","https://feeds.feedburner.com/ndtvnews-world-news"]


    # sql database
    db = SQL("sqlite:///news.db")

    #know the sentiment using aws
    comprehend = boto3.client(service_name='comprehend', region_name='us-west-2')

    ## get news from rss feed
    for i in range(len(agencies)):   
        print(agencies[i])
        feed = feedparser.parse(agencies[i])
        articles = feed.entries
        # author = articles.author_detail
        publisher = feed.feed.title

        for article in articles:
            title = article.title
            try:
                summary = article.summary
            except:
                pass
            link = article.link
            try:
                date = str(article.published_parsed[2]) + "/" + str(article.published_parsed[1]) + "/" + str(article.published_parsed[0])
            except:
                pass
            
            if(len(summary) == 0):
                sentiment = comprehend.detect_sentiment(Text = title, LanguageCode = 'en') #API call for sentiment analysis
            else:
                sentiment = comprehend.detect_sentiment(Text = summary, LanguageCode = 'en') #API call for sentiment analysis

            result = sentiment['Sentiment']
            # score = sentiment['SentimentScore']['Neutral'] * 100
            if result == "POSITIVE":
                score = int(sentiment['SentimentScore']['Positive'] * 100)
                
                rows = db.execute("SELECT * FROM news WHERE link = ?",link)
                if len(rows) == 0:
                    db.execute("INSERT INTO news(title,link,publisher,date,sentiment,score) VALUES(?,?,?,?,?,?)",title,link,publisher,date,result,score)
            
            if result == 'NEUTRAL':
                score = int(sentiment['SentimentScore']['Neutral'] * 100)
                
                rows = db.execute("SELECT * FROM news WHERE link = ?",link)
                if len(rows) == 0:
                    db.execute("INSERT INTO news(title,link,publisher,date,sentiment,score) VALUES(?,?,?,?,?,?)",title,link,publisher,date,result,score)
    return redirect("/")
