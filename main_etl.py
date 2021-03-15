from Real_time_sentiment_analysis_app import settings, credentials  # Import related setting constants from
# settings.py and api/access_token keys from credentials.py
import re
import tweepy
import mysql.connector
import pandas as pd
from textblob import TextBlob


# Streaming With Tweepy
# http://docs.tweepy.org/en/v3.4.0/streaming_how_to.html#streaming-with-tweepy

# Override tweepy.StreamListener to add logic to on_status
class MyStreamListener(tweepy.StreamListener):
    """
    Tweets are known as “status updates”. So the Status class in tweepy has properties describing the tweet.
    https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object.html
    """

    def on_status(self, status):
        """
        Extract info from tweets
        """

        if status.retweeted:
            # Avoid retweeted info, and only original tweets will be received
            return True
        # Extract attributes from each tweet
        id_str = status.id_str
        created_at = status.created_at
        text = deEmojify(status.text)  # Pre-processing the text
        sentiment = TextBlob(text).sentiment
        polarity = sentiment.polarity
        subjectivity = sentiment.subjectivity

        user_created_at = status.user.created_at
        user_location = deEmojify(status.user.location)
        user_description = deEmojify(status.user.description)
        user_followers_count = status.user.followers_count
        user_name = deEmojify(status.user.name)
        longitude = None
        latitude = None
        if status.coordinates:
            longitude = status.coordinates['coordinates'][0]
            latitude = status.coordinates['coordinates'][1]  # Me thinks this is how to access the json formatted
            # coordinates

        retweet_count = status.retweet_count
        favorite_count = status.favorite_count

        print(status.text)
        print("Long: {}, Lat: {}".format(longitude, latitude))

        # Store all data in MySQL
        if mydb.is_connected():
            mycursor = mydb.cursor()
            sql = "INSERT INTO {} (id_str, created_at, text, polarity, subjectivity, user_created_at, user_name, " \
                  "user_location, " \
                  "user_description, user_followers_count, longitude, latitude, retweet_count, favorite_count) VALUES " \
                  "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(settings.TABLE_NAME)

            val = (id_str, created_at, text, polarity, subjectivity, user_created_at, user_name, user_location,
                   user_description, user_followers_count, longitude, latitude, retweet_count, favorite_count)
            mycursor.execute(sql, val)
            mydb.commit()
            mycursor.close()

    def on_error(self, status_code):
        """
        Since Twitter API has rate limits, stop srcraping data as it exceed to the thresold.
        """
        if status_code == 420:
            # return False to disconnect the stream
            return False


def clean_tweet(self, tweet):
    """
    Use sumple regex statements to clean tweet text by removing links and special characters
    """
    return ' '.join(re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())


def deEmojify(text):
    """
    Strip all non-ASCII characters to remove emoji characters
    """
    if text:
        return text.encode('ascii', 'ignore').decode('ascii')
    else:
        return None


mydb = mysql.connector.connect(
    host="localhost",
    user="waleOpakunle",
    passwd="******", ## replace with your db details
    database="TwitterDB",
    charset='utf8'
)
if mydb.is_connected():
    '''
    Check if this table exits. If not, then create a new one.
    '''
    my_cursor = mydb.cursor()
    my_cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(settings.TABLE_NAME))
    if my_cursor.fetchone()[0] != 1:
        my_cursor.execute("CREATE TABLE {} ({})".format(settings.TABLE_NAME, settings.TABLE_ATTRIBUTES))
        mydb.commit()
    my_cursor.close()
