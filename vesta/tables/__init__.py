from sqlalchemy import select, or_, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

from vesta import POSTGRES
from .presentation import Presentation
from .users import User
from .custom_commands import CustomCommand
from .guild import Guild

engine = create_engine(f"postgresql://{POSTGRES}", )
