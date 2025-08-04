from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.types import TypeDecorator, TEXT
from sqlalchemy.ext.mutable import MutableDict
from db import Base
from utils.security import hash_password
import json

# Custom JSON type that works with SQLite
class JSONEncodedDict(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return json.loads(value)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String, default=None)
    created_at = Column(DateTime)
<<<<<<< Updated upstream
    platforms = Column(JSONEncodedDict)
=======

    # Use MutableDict to track changes inside JSON
    platforms = Column(MutableDict.as_mutable(JSONEncodedDict), default=dict)

>>>>>>> Stashed changes
    def set_password(self, password: str):
        self.password_hash = hash_password(password)
