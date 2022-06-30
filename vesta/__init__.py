import os
import discord
from sqlalchemy.orm import Session

TOKEN = os.getenv('TOKEN')
POSTGRES = os.getenv('POSTGRES')

from .tables import engine
session = Session(engine)

from .lang import Lang
from yaml import load, Loader
with open("vesta/data/lang.yml") as file:
    lang = Lang(load(file.read(), Loader), session)

from .client import Vesta

intents = discord.Intents.default()
intents.members = True
vesta_client = Vesta(intents=intents)
