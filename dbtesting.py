from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_SILENCE_UBER_WARNING=1

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    active = Column(Boolean, default=True)

if __name__ == "__main__":
    engine = create_engine('sqlite:///users.db')
    Base.metadata.create_all(bind=engine)
