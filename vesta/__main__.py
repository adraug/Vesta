from sqlalchemy import create_engine
from argparse import ArgumentParser

parser = ArgumentParser(prog="vesta", description="Vesta bot")
parser.add_argument("-t", "--token", required=True, help="The token of the bot")
parser.add_argument("-p", "--postgres", required=True)
parser.add_argument("-l", "--logging_level", type=int, default=20)
parser.add_argument("-v", "--verbose", action="store_const", const=10)

args = parser.parse_args()
if args.verbose:
    args.logging_level = args.verbose

from vesta import vesta_client, session_maker

engine = create_engine(f"postgresql://{args.postgres}")
session_maker.configure(bind=engine)


from vesta import commands
from vesta.tables import Base
from vesta.log import logger

logger.setLevel(args.logging_level)

Base.metadata.create_all(engine, checkfirst=True)

vesta_client.run(args.token)
