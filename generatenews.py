
from cs50 import SQL
import feedparser
import boto3




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
