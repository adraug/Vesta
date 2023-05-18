import sqlalchemy as db

from . import Base

class ClashOfCode(Base):
    __tablename__ = "clash_of_code"

    guild_id = db.Column(db.BigInteger, nullable=False)