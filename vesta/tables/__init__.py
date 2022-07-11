from sqlalchemy import select, or_
from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .presentations import Presentation
from .users import User
from .custom_commands import CustomCommand
from .guilds import Guild
from .bans import Ban