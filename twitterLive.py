import time
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import sqlite3
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from unidecode import unidecode


analyzer = SentimentIntensityAnalyzer()

# consumer key, consumer secret, access token, access secret.
ckey = "AeiEWXqrh9TEZpMK6D3JXgYeR"
csecret = "IA3ACrYMSOZqcOcWOguQBwOsy47VZCEvGLBYauVr0iWbO4Dehr"
atoken = "381209092-08RQEfpldp6hoZTqCZu2LztCZ6Ub6y1YII1OUkxa"
asecret = "WkZaxwbeZmmUWOZR7tM5wk2CePTuI4LF9laV04NvayXor"


conn = sqlite3.connect('twitter.db')
c = conn.cursor()

def create_table():
    try:
        c.execute("CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT, sentiment REAL)")
        c.execute("CREATE INDEX fast_unix ON sentiment(unix)")
        c.execute("CREATE INDEX fast_tweet ON sentiment(tweet)")
        c.execute("CREATE INDEX fast_sentiment ON sentiment(sentiment)")
        conn.commit()
    except Exception as e:
        print(str(e))


create_table()


class listener(StreamListener):

    def on_data(self, data):
        try:
            data = json.loads(data)
            tweet = unidecode(data['text'])
            time_ms = data['timestamp_ms']
            vs = analyzer.polarity_scores(tweet)
            sentiment = vs['compound']
            print(time_ms, sentiment)
            c.execute("INSERT INTO sentiment (unix, tweet, sentiment) VALUES (?, ?, ?)",
                      (time_ms, tweet, sentiment))
            conn.commit()

        except KeyError as e:
            print(str(e))
        return True

    def on_error(self, status):
        print(status)


while True:
    try:
        auth = OAuthHandler(ckey, csecret)
        auth.set_access_token(atoken, asecret)
        twitterStream = Stream(auth, listener())
        twitterStream.filter(track=["StopRobbingUs"])
    except Exception as e:
        print(str(e))
        time.sleep(5)



