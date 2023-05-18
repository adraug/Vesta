import logging

from .tables import select, Guild

logger = logging.getLogger(__name__)

class Lang:

    def __init__(self, data, session):
        self.data = data
        self.session = session

    def get(self, item, guild):
        lang = "en"

        if guild.preferred_locale[:2] in self.data:
            lang = guild.preferred_locale[:2]

        r = select(Guild).where(Guild.id == guild.id)

        with self.session() as session:
            search_guild = session.scalar(r)

        if search_guild and search_guild.lang:
            lang = search_guild.lang

        if item in self.data[lang]:
            return self.data[lang][item]

        logger.error(f"Element {item} not found : guild {guild}, lang {lang}")
        return "Could not load"
