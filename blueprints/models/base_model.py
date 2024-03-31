from uuid import uuid4
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime
from blueprints.models import *

STORAGE_TYPE = 'db'  # Hard-coded storage type

if STORAGE_TYPE == 'db':
    Base = declarative_base()
else:
    class Base:
        pass

class BaseModel:
    """
    Attributes and functions for BaseModel class.
    """

    if STORAGE_TYPE == 'db':
        id = Column(String(60), nullable=False, primary_key=True)
        created_at = Column(DateTime, nullable=False, default=datetime.utcnow())
        updated_at = Column(DateTime, nullable=False, default=datetime.utcnow())

    def __init__(self, *args, **kwargs):
        """
        Instantiation of new BaseModel class.
        """
        if kwargs:
            self.__set_attributes(kwargs)
        else:
            self.id = str(uuid4())
            self.created_at = datetime.utcnow()

    def __set_attributes(self, attr_dict):
        """
        Private: converts attr_dict values to Python class attributes.
        """
        if 'id' not in attr_dict:
            attr_dict['id'] = str(uuid4())
        if 'created_at' not in attr_dict:
            attr_dict['created_at'] = datetime.utcnow()
        if 'updated_at' not in attr_dict:
            attr_dict['updated_at'] = datetime.utcnow()
        for attr, val in attr_dict.items():
            setattr(self, attr, val)

    def save(self):
        """
        Updates attribute updated_at to current time.
        """
        self.updated_at = datetime.utcnow()
        models.storage.new(self)
        models.storage.save()

    def delete(self):
        """
        Deletes current instance from storage.
        """
        models.storage.delete(self)
