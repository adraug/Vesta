from typing import Optional

import sqlalchemy as db

from . import Base
from .. import session_maker
from ..services import clash_of_code_helper, ClashOfCodeGame

session = session_maker()

class ClashOfCodeGuildGame(Base):
    __tablename__ = "clash_of_code_guild_game"

    guild_id = db.Column(db.BigInteger, nullable=False, primary_key=True)
    last_clash_id = db.Column(db.String(511), nullable=True)
    announcement_message_id = db.Column(db.BigInteger, nullable=True)

    def fetch(self) -> Optional[ClashOfCodeGame]:
        """
        Fetches the latest clash of code game

        :return: The latest clash of code game
        """

        return clash_of_code_helper.fetch(self.last_clash_id)

    def __repr__(self):
        return f"Clash of Code Guild Games (guild_id={self.guild_id}, last_clash_id={self.last_clash_id})"
