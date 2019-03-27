from tweepy import Cursor
from tweepy import API
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob
import numpy as np
import re
import pandas as pd
import matplotlib.pyplot as plt
import Twitter_Credentials
desired_width = 320
pd.set_option('display.width', desired_width)
pd.set_option("display.max_columns", 10)


class TwitterClient:
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator.authenticate_twitter_app(self)
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)

        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self,num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


class TwitterAuthenticator:
    """
    This class handles the authentication.
    """

    def authenticate_twitter_app(self):
        auth = OAuthHandler(consumer_key=Twitter_Credentials.CONSUMER_KEY,
                            consumer_secret=Twitter_Credentials.CONSUMER_SECRET)
        auth.set_access_token(Twitter_Credentials.ACCESS_TOKEN, Twitter_Credentials.ACCESS_TOKEN_SECRET)
        return auth


class TwitterStreamer:

    """
    This class handles the streaming and processing of tweets
    """
    def __init__(self):
        self.twitter_authenticate = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # this handles the authentication and connection to twitter Streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticate.authenticate_twitter_app()
        stream = Stream(auth, listener)

        # this filters the tweets stream to capture the ones we need
        stream.filter(track=hash_tag_list)


class TwitterListener(StreamListener):

    """
    This class prints the received tweets to stdout
    """

    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True

    def on_error(self, status_code):
        print(status_code)

class TweetAnalyser():
    """
    Analyse and categorise tweets.
    """

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyse_tweet_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1



    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        return df


if __name__ == "__main__":
    twitter_client = TwitterClient()
    twitter_analyser = TweetAnalyser()
    api = twitter_client.get_twitter_client_api()
    tweets = api.user_timeline(screen_name="realDonaldTrump", count=400)
    df = twitter_analyser.tweets_to_data_frame(tweets)
    df['sentiment'] = np.array([twitter_analyser.analyse_tweet_sentiment(tweet) for tweet in df['Tweets']])
    print(df.head(10))
    df.to_csv('DonaldTweet.csv' , index=False)



    """
    print(np.max(df['len']))
    print(np.max(df['likes']))
    
    
    time_likes = pd.Series(data=df['likes'].values, index=df['date'])
    time_likes.plot(figsize=(16,4), color='red')
    plt.show()

    time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
    time_retweets.plot(figsize=(16, 4), color='green')
    plt.show()
    
    time_likes = pd.Series(data=df['likes'].values, index=df['date'])
    time_likes.plot(figsize=(16, 4), label="likes", legend=True)

    time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
    time_retweets.plot(figsize=(16, 4), label="retweets",legend=True)
    plt.yticks(np.arange(min(time_likes), max(time_likes) + 1, 20000))
    plt.show()
    """


