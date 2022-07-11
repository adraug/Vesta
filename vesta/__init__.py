import discord
from sqlalchemy.orm import sessionmaker


session_maker = sessionmaker()

from .lang import Lang
from yaml import load, Loader
with open("vesta/data/lang.yml") as file:
    lang = Lang(load(file.read(), Loader), session_maker)

from .client import Vesta

intents = discord.Intents.default()
intents.members = True
vesta_client = Vesta(intents=intents)
