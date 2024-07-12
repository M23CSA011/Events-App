from .database import Base
from sqlalchemy import Column , Integer , String ,Boolean,ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP 
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship

class Registration(Base):
    __tablename__="registrations"

    id = Column(Integer,primary_key=True,nullable=False)
    event_id = Column(Integer,ForeignKey('events.id',ondelete="CASCADE"),nullable=False)
    name = Column(String,nullable=False)
    age = Column(Integer,nullable=False)
    gender = Column(String,nullable=False)
    user_registered_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    user_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    user = relationship("User")
    event = relationship("Event")

class Event(Base):
    __tablename__="events"

    id = Column(Integer,primary_key=True,nullable=False)
    title = Column(String,nullable=False)
    description = Column(String,nullable=False)
    location = Column(String,nullable=False)
    price = Column(Integer,nullable=False)
    event_datetime = Column(TIMESTAMP(timezone=True),nullable=False)
    event_created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    owner_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    user = relationship("User")

class User(Base):
    __tablename__="users"
    id = Column(Integer,primary_key=True,nullable=False)
    email = Column(String,nullable=False,unique=True)
    name = Column(String,nullable=False)
    password = Column(String,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    role=Column(String,nullable=False)







