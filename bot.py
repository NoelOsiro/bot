from blueprints.models import storage
from blueprints.models.tweet import Tweet, TweetImage
from blueprints.utils.post import TwitterBot, NoTweetsFoundError


def bot_post():
    """
    Task to post a tweet using the TwitterBot class.

    Returns:
        None
    """
    # Create an instance of TwitterBot
    bot = TwitterBot()

    try:
        # Get a tweet from storage
        tweet = bot.get_tweets()
    except NoTweetsFoundError:
        print("No tweets are ready to be posted.")
        # Exit the function if no tweets are found
        return

    # Get the text content of the tweet
    tweet_text = bot.get_text(tweet)

    # Prepare tweet data dictionary
    tweet_data = {
        'tweet_text': tweet_text,
        'id': tweet.id,
        'title': tweet.title,
    }

    # Create and post the tweet
    bot.create_and_post_tweet(tweet_data)

    # Update the tweet status to posted
    bot.update_tweet_status(tweet.id)

    # Clean up temporary files and directories
    bot.cleanup()
