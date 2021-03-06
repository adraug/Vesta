import sqlalchemy as db
from sqlalchemy.orm import relationship

from . import Base


class User(Base):
    __tablename__ = "user"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    avatar_url = db.Column(db.String(127), nullable=False)

    def __repr__(self):
        return f"User(id={self.id}, name={self.name})"

    presentations = relationship("Presentation", back_populates="author")
