import sqlalchemy as db
from sqlalchemy.orm import declarative_base, relationship

from . import Base


class User(Base):
    __tablename__ = "user"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    avatar_url = db.Column(db.String(127), nullable=False)
    moderator = db.Column(db.Boolean(), default=False, nullable=False)
    presentations_banned = db.Column(db.Boolean(), default=False, nullable=False)
    nicknames_banned = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, moderator={self.moderator}, banned={self.banned})"

    presentations = relationship("Presentation", back_populates="author")