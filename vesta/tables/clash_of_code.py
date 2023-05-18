import time

import sqlalchemy as db
from sqlalchemy.orm import relationship

from . import Base

class ClashOfCode(Base):
    __tablename__ = "clash_of_code"

    guild_id = db.Column(db.BigInteger, db.ForeignKey("guild.id"), nullable=False)
    guild = relationship("Guild")

    last_time_used = db.Column(db.DateTime, nullable=False)

    db.PrimaryKeyConstraint(guild_id)

    def is_usable(self) -> bool:
        if not self.last_time_used: return True

        return time.mktime(self.last_time_used.timetuple()) + self.guild.coc_cooldown >= time.time()