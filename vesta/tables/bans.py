import sqlalchemy as db

from . import Base


class Ban(Base):
    __tablename__ = "ban"

    user_id = db.Column(db.BigInteger, nullable=False)
    guild_id = db.Column(db.BigInteger, nullable=False)
    presentation_banned = db.Column(db.Boolean, default=False)
    nickname_banned = db.Column(db.Boolean, default=False)

    db.PrimaryKeyConstraint(user_id, guild_id)

    def __repr__(self):
        return f"Guild(user={self.user_id}, guild={self.guild_id}, presentation_banned={self.presentation_banned}, nickname_banned={self.nickname_banned})"
