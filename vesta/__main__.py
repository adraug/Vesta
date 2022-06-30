from vesta import TOKEN, vesta_client, engine
from vesta import commands
from .tables import Base

vesta_client.run(TOKEN)

Base.metadata.create_all(engine, checkfirst=True)
