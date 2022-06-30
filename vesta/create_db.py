import os

from sqlalchemy import create_engine
from tables import Base

POSTGRES = os.getenv('POSTGRES')

engine = create_engine(f"postgresql://{POSTGRES}", )

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

