from blueprints.models.base_model import BaseModel
from blueprints.models.tweet import Tweet
from blueprints.models.user import User


STORAGE_TYPE = 'db'  # Hard-coded storage type

if STORAGE_TYPE == 'db':
    from blueprints.models.engine import db_storage  
    storage = db_storage.DBStorage()

storage.reload()
