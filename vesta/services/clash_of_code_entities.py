from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

from discord import Embed

from vesta import lang


class GameMode(Enum):
    """
    Represents a Clash of Code game mode
    """

    FASTEST = 0
    REVERSE = 1
    SHORTEST = 2


class Role(Enum):
    """
    Represents a Clash of Code player role
    """

    OWNER = 0
    STANDARD = 1


@dataclass
class ClashOfCodePlayer:
    """
    Represents a player in a Clash of Code game
    """

    name: str
    role: Role

    def __init__(self, **kwargs):
        """
        Initializes the object with the given data

        :param kwargs: The data to initialize the object with
        :see hydrate
        """
        self.hydrate(**kwargs)

    def hydrate(self, *,
                codingamerNickname: str,
                status: str,
                **ignored) -> "ClashOfCodePlayer":
        """
        Hydrates the object with the given data

        :param codingamerNickname: The player's nickname
        :param status: The player's role
        :return: The hydrated object for chaining convenience
        """
        self.name = codingamerNickname
        self.role = Role[status.upper()] or Role.STANDARD

        return self


@dataclass
class ClashOfCodeGame:
    """
    Represents a Clash of Code game
    """

    link: str
    started: bool
    finished: bool
    players: List[ClashOfCodePlayer]
    programming_language: List[str]
    modes: List[GameMode]
    mode: Optional[str]

    def __init__(self, **kwargs):
        """
        Initializes the object with the given data
        :param kwargs: The data to initialize the object with
        :see hydrate
        """

        self.hydrate(**kwargs)

    def hydrate(self, *,
                publicHandle: str,
                started: bool,
                finished: bool,
                players: List[dict],
                programmingLanguages: List[str],
                modes: List[str],
                mode: Optional[str] = None,
                **ignored) -> "ClashOfCodeGame":
        """
        Hydrates the object with the given data

        :param publicHandle: The game id
        :param started: Whether the game has started
        :param finished: Whether the game has finished
        :param players: The players in the game
        :param programmingLanguages: The programming languages used in the game
        :param modes: The possible game modes
        :param mode: The current game mode. Only defined if started is True
        :return: The hydrated object for chaining convenience
        """

        self.link = f"https://www.codingame.com/clashofcode/clash/{publicHandle}"
        self.started = started
        self.finished = finished
        self.players = [
            ClashOfCodePlayer(**player)
            for player in players
        ]
        self.programming_language = programmingLanguages
        self.modes = [
            GameMode[mode.upper()]
            for mode in modes
        ]
        self.mode = mode

        return self

    def embed(self):
        emojis = {
            'True': '🟢',
            'False': '🔴'
        }

        description = f"""
        **{lang.get("clash_of_code_game.started")}** {emojis[str(self.started)]}
        **{lang.get("clash_of_code_game.finished")}** {emojis[str(self.finished)]}
        """

        embed = Embed(
            title=lang.get("clash_of_code.game_title"),
            url=self.link,
            description=description
        )

        if not self.mode:
            embed.add_field(name=lang.get("clash_of_code.game_modes"),
                            value=f"`{'`, `'.join([mode.name.lower() for mode in self.modes])}`")
        else:
            embed.add_field(name=lang.get("clash_of_code.game_mode"),
                            value=f"`{self.mode.lower()}`")

        embed.add_field(name=lang.get("clash_of_code.game_players"),
                        value=f"`{'`, `'.join([player.name for player in self.players])}`")

        languages = f"`{'`, `'.join(self.programming_language)}`" \
                        if len(self.programming_language) >= 1 \
                        else lang.get("clash_of_code.all_languages")

        embed.add_field(name=lang.get("clash_of_code.game_languages"),
                        value=languages)
