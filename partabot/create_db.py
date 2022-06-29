import os
from sqlalchemy.orm import declarative_base, Session

from sqlalchemy import create_engine
from tables.users import User
from tables.presentation import Presentation
from tables import Base

POSTGRES = os.getenv('POSTGRES')

engine = create_engine(f"postgresql://{POSTGRES}", )

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
#
# session = Session(engine)
# billy = User(
#     id=42,
#     name="Billy",
#     avatar_url="https://i.imgur.com/w3duR07.png",
# )
# print(billy)
# session.add(billy)
# session.commit()
# print(session.query(User).all())



