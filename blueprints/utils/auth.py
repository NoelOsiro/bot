import os
import tweepy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

api_key=os.getenv('TWITTER_API_KEY')
api_secret=os.getenv('TWITTER_API_SECRET')
access_token=os.getenv('TWITTER_ACCESS_TOKEN')
access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

def get_twitter_conn_v1() -> tweepy.API:
    """Get twitter conn 1.1"""

    auth = tweepy.OAuth1UserHandler(api_key, api_secret)
    auth.set_access_token(
        access_token,
        access_token_secret,
    )
    return tweepy.API(auth)

def get_twitter_conn_v2() -> tweepy.Client:
    """Get twitter conn 2.0"""

    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )

    return client

