import os
import discord
from sqlalchemy.orm import Session


TOKEN = os.getenv('TOKEN')
GUILD = discord.Object(id=os.getenv('GUILD'))
REVIEW_CHANNEL = int(os.getenv('REVIEW_CHANNEL'))
POST_CHANNEL = int(os.getenv('POST_CHANNEL'))
POSTGRES = os.getenv('POSTGRES')

from partabot.tables import engine
session = Session(engine)

from partabot.client import PartaBot

intents = discord.Intents.default()
intents.members = True
partabot_client = PartaBot(intents=intents)
