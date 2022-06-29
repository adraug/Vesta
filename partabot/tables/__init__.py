from sqlalchemy import select, or_, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

from partabot import POSTGRES
from .presentation import Presentation
from .users import User

engine = create_engine(f"postgresql://{POSTGRES}", )
