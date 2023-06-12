from sqlalchemy import create_engine
from sqlalchemy import  Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.orm import backref, relationship


class Base(DeclarativeBase): pass


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True)
    username = Column(String, default="")
    # photo_path = Column(String, default="")

    def __str__(self):
        return f"{ self.id } - { self.username }"

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="Wait")
    id_admin = Column(ForeignKey("persons.id"))
    players_in_room = relationship("Players", cascade="all,delete", backref="Room", lazy="joined")
    # photo_path = Column(String, default="")

class Players(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    id_room = Column(ForeignKey("rooms.id"))
    id_user = Column(ForeignKey("persons.id"))
    score = Column(Integer, default=0)
    target_list = Column(String, default="")
    # photo_path = Column(String, default="")


class Targets(Base):
    __tablename__ = "targets"
    id = Column(Integer, primary_key=True, index=True)
    id_room = Column(ForeignKey("rooms.id"))
    target_user = Column(ForeignKey("persons.id"))
    id_user = Column(ForeignKey("persons.id"))