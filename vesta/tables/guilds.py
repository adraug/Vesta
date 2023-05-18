import sqlalchemy as db

from . import Base


class Guild(Base):
    __tablename__ = "guild"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    review_channel = db.Column(db.BigInteger)
    projects_channel = db.Column(db.BigInteger)
    coc_channel = db.column(db.BigInteger)
    coc_role = db.Column(db.BigInteger)
    lang = db.Column(db.String(2))

    def __repr__(self):
        return f"Guild(id={self.id}, name={self.name})"
