import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from blueprints.models.base_model import Base
from blueprints.models.user import User
from blueprints.models.tweet import Tweet

DB_URI = 'sqlite:///database.db'

class DBStorage:
    """
    Handles long term storage of User and Tweet instances using SQLite.
    """
    __engine = None
    __session = None

    def __init__(self):
        """
        Initializes the SQLite database engine.
        """
        self.__engine = create_engine(DB_URI)
        Base.metadata.create_all(self.__engine)
        Session = sessionmaker(bind=self.__engine)
        self.__session = Session()

    def all(self, cls=None):
        """
        Returns a dictionary of all User or Tweet objects, or both if cls is None.
        """
        obj_dict = {}
        classes = [User, Tweet] if cls is None else [cls]
        for c in classes:
            for obj in self.__session.query(c):
                obj_ref = f"{type(obj).__name__}.{obj.id}"
                obj_dict[obj_ref] = obj
        return obj_dict

    def new(self, obj):
        """
        Adds objects to the current database session.
        """
        self.__session.add(obj)

    def save(self):
        """
        Commits all changes of the current database session.
        """
        self.__session.commit()

    def delete(self, obj=None):
        """
        Deletes obj from the current database session if not None.
        """
        if obj:
            self.__session.delete(obj)

    def get(self, cls, filters):
        """
        Retrieves one object based on class and filters.
        """
        obj_query = self.__session.query(cls)
        for attr, value in filters.items():
            obj_query = obj_query.filter(getattr(cls, attr) == value)
        return obj_query.first()

    def get_all(self, cls, filters):
        """
        Retrieves all object based on class and filters.
        """
        obj_query = self.__session.query(cls)
        for attr, value in filters.items():
            obj_query = obj_query.filter(getattr(cls, attr) == value)
        return obj_query.all()
    
    def count(self, cls=None):
        """
        Returns the count of all objects in storage.
        """
        return len(self.all(cls))

    def rollback(self):
        """
        Creates arollback changes on the session.
        """
        return self.__session.rollback

    def reload(self):
        """
        Creates all tables in the database and refreshes the session.
        """
        Base.metadata.create_all(self.__engine)
        self.__session = sessionmaker(bind=self.__engine)()

    def close(self):
        """
        Closes the session.
        """
        self.__session.close()
