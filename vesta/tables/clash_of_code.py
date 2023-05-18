from typing import Optional

import sqlalchemy as db
from sqlalchemy.orm import relationship

from . import Base
from .. import session_maker
from ..services.clash_of_code_entities import ClashOfCodeGame
from ..services.clash_of_code_helper import ClashOfCodeHelper

session = session_maker()

class ClashOfCodeGuildGame(Base):
    __tablename__ = "clash_of_code_guild_game"

    guild_id = db.Column(db.BigInteger, nullable=False)
    last_clash_id = db.Column(db.BigInteger)

    db.PrimaryKeyConstraint(guild_id)

    def fetch(self) -> Optional[ClashOfCodeGame]:
        """
        Fetches the latest clash of code game

        :return: The latest clash of code game
        """

        helper = ClashOfCodeHelper()

        return helper.fetch(self.last_clash_id)

    def can_start_new(self) -> bool:
        """
        Checks whether a new clash of code game can be started

        :return: Whether a new clash of code game can be started
        """
        if self.last_clash_id is None:
            return True

        entity = self.fetch()
        return entity is None or entity.finished

    def __repr__(self):
        return f"Clash of Code Guild Games (guild_id={self.guild_id}, last_clash_id={self.last_clash_id})"

    def forget(self) -> None:
        """
        Forgets the last clash of code game
        :return: None
        """
        self.last_clash_id = None
        session.commit()

    def start_new(self, clash_id: int) -> None:
        """
        Starts a new clash of code game

        :param clash_id: The clash of code game id
        :return: None
        """
        self.last_clash_id = clash_id
        session.commit()

class ClashOfCodeRanking(Base):
    __tablename__ = "clash_of_code_ranking"

    guild_id = db.Column(db.BigInteger, nullable=False)
    times_won = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.BigInteger, db.ForeignKey("user.id"), nullable=False)
    user = relationship("User")

    db.PrimaryKeyConstraint(guild_id, user_id)

    def add_win(self) -> None:
        """
        Adds a win to the user's ranking and commits the change to the database
        :return: None
        """
        self.times_won += 1
        session.commit()

    def __repr__(self):
        return f"Clash of Code Ranking (guild_id={self.guild_id}, user_id={self.user_id}, times_won={self.times_won})"