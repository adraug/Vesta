import logging
from typing import MutableMapping

from .tables import select, Guild

logger = logging.getLogger(__name__)

class Lang:
    data: dict

    def __init__(self, data, session):
        self.data = data
        self.session = session

        def flatten_dict(d: MutableMapping, parent_key: str = '', sep: str = '.') -> MutableMapping:
            items = []
            for k, v in d.items():
                new_key = parent_key + sep + k if parent_key else k
                if isinstance(v, MutableMapping):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)

        for key in self.data.keys():
            self.data[key] = flatten_dict(self.data[key])

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
