from vesta import TOKEN, vesta_client, engine
from vesta import commands
from .tables import Base

Base.metadata.create_all(engine, checkfirst=True)

vesta_client.run(TOKEN)
