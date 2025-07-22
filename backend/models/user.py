from db import Base
from sqlalchemy import Column, Integer, String, DateTime
import json
from sqlalchemy.types import TypeDecorator, TEXT

# Custom JSON Type for SQLite
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
    platforms = Column(JSONEncodedDict)
