from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from blueprints.models.base_model import Base

class Tweet(Base):
    """
    Tweet class handles tweets in the application.
    """
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    text = Column(String(1000), nullable=False)
    status = Column(Boolean, default=False)

    images = relationship('TweetImage', backref='tweet', cascade='all, delete-orphan')

    def __init__(self, title, text,status=False, images=None):
        """
        Initializes a tweet object.
        """
        self.title = title
        self.text = text
        self.status = status
        if images:
            self.images = [TweetImage(url=image_url) for image_url in images]

    def __repr__(self):
        """
        Returns a string representation of the tweet object.
        """
        return f'<Tweet(id={self.id}, title={self.title}, text={self.text})>'

class TweetImage(Base):
    """
    TweetImage class handles image URLs associated with tweets.
    """
    __tablename__ = 'tweet_images'

    id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer, ForeignKey('tweets.id'), nullable=False)
    url = Column(String(255), nullable=False)
    status = Column(Boolean, default=False)


    def __init__(self, url):
        """
        Initializes a tweet image object.
        """
        self.url = url

    def __repr__(self):
        """
        Returns a string representation of the tweet object.
        """
        return f'<Tweet(id={self.id}, tweet_id={self.tweet_id}, url={self.url}, status={self.status})>'