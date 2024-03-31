import os
import shutil
import requests
from blueprints.utils.auth import get_twitter_conn_v1, get_twitter_conn_v2
from blueprints.models.tweet import Tweet, TweetImage
from blueprints.models import storage
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class NoTweetsFoundError(Exception):
    """Exception raised when no tweets are found."""
    pass

class TwitterBot:
    """
    Class for managing Twitter bot operations, including tweeting with images.
    """

    def __init__(self):
        """
        Initialize TwitterBot with Twitter API connections and config settings.
        """
        self.client_v1 = get_twitter_conn_v1()
        self.client_v2 = get_twitter_conn_v2()
        self.max_attempts = 7
        self.img_size = 'large'
        self.media_folder = 'temp_images/'
        self.google_key = os.getenv('GOOGLE_API_KEY')
        self.cx = os.getenv('GOOGLE_CX')

    def get_tweets(self) -> list:
        """
        Get tweets that are ready to be posted.

        Returns:
            list: List of tweets ready for posting.

        Raises:
            NoTweetsFoundError: Raised when no tweets are found.
        """
        tweet = storage.get(Tweet, {'status': False})
        if tweet is None:
            raise NoTweetsFoundError("No tweets ready to be posted.")
        return tweet

    def get_text(self, tweet):
        """
        Get text content from a tweet.

        Args:
            tweet: Tweet object containing title and text.

        Returns:
            str: Text content of the tweet.
        """
        if tweet is None:
            return None
        tweet_text = f"{tweet.title}\n{tweet.text}"
        tweet_text_sets = self.split_text(tweet_text)
        return tweet_text_sets

    def split_text(self, text: str):
        """
        Split text into sets of 280 characters without splitting words.

        Args:
            text (str): Text to split.

        Returns:
            list: List of split text sets.
        """
        max_chars = 280
        text_sets = []
        while len(text) > max_chars:
            # Find the last space before max_chars
            split_index = text.rfind(' ', 0, max_chars)
            if split_index == -1:
                text_sets.append(text[:max_chars])
                text = text[max_chars:]
            else:
                text_sets.append(text[:split_index])
                text = text[split_index + 1:]
        text_sets.append(text)
        return text_sets

    def get_images(self, tweet_id):
        """
        Get image URLs for a tweet.

        Args:
            tweet_id: ID of the tweet.

        Returns:
            list: List of image URLs.
        """
        tweet_images = storage.get_all(TweetImage, {'tweet_id': tweet_id})
        urls = []
        if tweet_images is None:
            raise NoTweetsFoundError("No images ready to be posted.")
        for image in tweet_images:
            urls.append(image.url)
        return urls

    def send_api_request(self, search, attempt, img_size=None):
        """
        Send an API request to search for images.

        Args:
            search (str): Search query.
            attempt (int): Number of attempts for the API request.
            img_size (str, optional): Image size. Defaults to None.

        Returns:
            str: Filename of the downloaded image.
        """
        base_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.google_key,
            "q": search,
            "cx": self.cx,
            "num": attempt,
            "searchType": 'image',
            "imgSize": img_size,
        }

        response = requests.get(base_url, params=params)
        data = response.json()
        index = attempt - 1

        if 'items' in data:
            items_dict = data['items'][index]
            if 'link' in items_dict:
                image_url = items_dict['link']
                try:
                    image_response = requests.get(image_url, timeout=10)
                    image_response.raise_for_status()

                    # Save the image to a file
                    with open('temp_images/abc.jpg', 'wb') as image_file:
                        image_file.write(image_response.content)

                    return 'abc.jpg'
                except requests.exceptions.RequestException as e:
                    raise Exception(f"Error downloading image: {e}")
        elif 'error' in data:
            raise Exception(f"API Error: {data['error']['message']}")
        else:
            raise Exception("No 'items' in the JSON response.")

    def download_images(self, tweet_id):
        """
        Download images ready for upload in temporary storage.

        Args:
            tweet_id: ID of the tweet.

        Returns:
            str: Path to the temporary dir containing the downloaded images.
        """
        images = self.get_images(tweet_id)
        temp_dir = 'temp_images'

        for idx, image_url in enumerate(images):
            try:
                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                    file_name = f"image_{tweet_id}_{idx}.jpg"
                    file_path = os.path.join(temp_dir, file_name)

                    with open(file_path, "wb") as file:
                        shutil.copyfileobj(response.raw, file)
                else:
                    print(f"Failed to download image: {image_url}")
            except Exception as e:
                print(f"Error downloading image: {e}")

        return temp_dir

    def create_and_post_tweet(self, tweet_data):
        """
        Create and post a tweet with images and text.

        Args:
            tweet_data (dict): Dictionary containing
            tweet data, including ID, title, text, and image URLs.

        Returns:
            None
        """
        if tweet_data is None:
            raise NoTweetsFoundError("No tweets ready to be posted.")
        if not os.path.exists(self.media_folder):
            os.makedirs(self.media_folder)
        self.download_images(tweet_data['id'])

        attempt = 1
        while attempt <= self.max_attempts:
            api_response = self.send_api_request(
                tweet_data['title'],
                attempt, self.img_size)

            if api_response is None:
                print(f"Error: No image found for tweet {tweet_data['id']}")
                return

            media_ids = self.upload_media_files()
            if media_ids is None:
                print("Error uploading media files.")
                return

            tweet_text = tweet_data.get('tweet_text', [])
            self.post_tweet(media_ids, tweet_text)

            print(f"Success - Tweet No: {tweet_data['id']} has been posted")
            return

        print(f"Max attempt ({self.max_attempts}) reached {tweet_data['id']}.")

    def upload_media_files(self):
        """
        Upload media files (images) to Twitter.

        Returns:
            list: List of media IDs for uploaded images.
        """
        media_ids = []
        for file_name in os.listdir(self.media_folder):
            media_path = os.path.join(self.media_folder, file_name)
            if os.path.isfile(media_path):
                media = self.client_v1.simple_upload(filename=media_path)
                media_ids.append(media.media_id)
                # Remove the individual image file after upload
                os.remove(media_path)

        return media_ids if media_ids else None

    def post_tweet(self, media_ids, tweet_text):
        """
        Post a tweet with images and text to Twitter.

        Args:
            media_ids (list): List of media IDs for uploaded images.
            tweet_text (list): List of text content for the tweet.

        Returns:
            None
        """
        if len(tweet_text) > 0:
            tweet = self.client_v2.create_tweet(
                media_ids=media_ids,
                text=tweet_text[0])
            for reply_text in tweet_text[1:]:
                self.client_v2.create_tweet(
                    text=reply_text,
                    in_reply_to_tweet_id=tweet.data['id'])
        else:
            self.client_v2.create_tweet(media_ids=media_ids)

    def update_tweet_status(self, tweet_id:int):
        """
        Update a tweet with status to true.

        Args:
            tweet_id (int): List of text content for the tweet.

        Returns:
            None
        """
        tweet = storage.get(Tweet, {'id': tweet_id})
        if tweet is None:
            print("Tweet not found.")
            return
        else:
            tweet.status = True
            storage.new(tweet)
            storage.save()

    def cleanup(self):
        """
        Cleanup temporary files and directories after tweeting.

        Returns:
            None
        """
        if os.path.exists(self.media_folder):
            shutil.rmtree(self.media_folder)

bot =TwitterBot()
bot.update_tweet_status(1)