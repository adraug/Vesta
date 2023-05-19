import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

import discord
from discord import Embed


class GameMode(Enum):
    """
    Represents a Clash of Code game mode
    """

    FASTEST = 0
    REVERSE = 1
    SHORTEST = 2

    def __repr__(self):
        return f"coc_mode_{self.name.lower()}"

class Role(Enum):
    """
    Represents a Clash of Code player role
    """

    OWNER = 0
    STANDARD = 1

class State(Enum):
    """
    Represents a Clash of Code game state
    """

    PENDING = 0
    RUNNING = 1
    FINISHED = 2

    def __repr__(self):
        """
        Gives the translation key for the state
        """
        return f"coc_game_state_{self.name.lower()}"

    def __str__(self):
        """
        Gives the emoji for the state
        """
        return {
            State.PENDING: "🕒",
            State.RUNNING: "🔥",
            State.FINISHED: "🏁"
        }[self]

@dataclass
class ClashOfCodePlayer:
    """
    Represents a player in a Clash of Code game
    """

    name: str
    role: Role
    rank: int
    state: State

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
                rank: Optional[int],
                testSessionStatus: Optional[str] = None,
                **ignored) -> "ClashOfCodePlayer":
        """
        Hydrates the object with the given data

        :param codingamerNickname: The player's nickname
        :param status: The player's role
        :return: The hydrated object for chaining convenience
        """
        self.name = codingamerNickname
        self.role = Role[status.upper()] or Role.STANDARD
        self.rank = rank
        self.state = State.PENDING if testSessionStatus is None\
            else State.FINISHED if testSessionStatus == "COMPLETED" \
            else State.RUNNING

        return self


@dataclass
class ClashOfCodeGame:
    """
    Represents a Clash of Code game
    """

    link: str
    state: State
    players: List[ClashOfCodePlayer]
    programming_language: List[str]
    modes: List[GameMode]
    mode: Optional[GameMode]

    start_time: datetime.datetime
    end_time: Optional[datetime.datetime]

    def __init__(self, **kwargs):
        """
        Initializes the object with the given data
        :param kwargs: The data to initialize the object with
        :see hydrate
        """

        self.hydrate(**kwargs)

    @property
    def id(self): return self.link.split("/")[-1]

    def hydrate(self, *,
                publicHandle: str,
                started: bool,
                finished: bool,
                players: List[dict],
                programmingLanguages: List[str],
                modes: List[str],
                mode: Optional[str] = None,
                startTime: str,
                endTime: Optional[str] = None,
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
        self.state = State.FINISHED if finished else State.RUNNING if started else State.PENDING
        self.players = [
            ClashOfCodePlayer(**player)
            for player in players
        ]
        self.programming_language = programmingLanguages
        self.modes = [
            GameMode[mode.upper()]
            for mode in modes
        ]
        self.mode = GameMode[mode.upper()] if mode else None

        self.start_time = datetime.datetime.strptime(startTime, "%B %d, %Y, %I:%M:%S %p")
        self.end_time = datetime.datetime.strptime(endTime, "%B %d, %Y, %I:%M:%S %p") if endTime else None

        return self

    def embed(self, guild: discord.Guild):
        """
        Builds a legible embed to display on discord

        :param guild:
        :return:
        """
        from .. import lang_file

        embed = Embed(
            title=lang_file.get("coc_game_title", guild),
            color=discord.Color.blurple(),
        )

        embed.add_field(name=lang_file.get("coc_game_state", guild),
                        value=lang_file.get(repr(self.state), guild),
                        inline=True)

        if not self.mode:
            embed.add_field(name=lang_file.get("coc_game_modes", guild),
                            value=' - ' + "\n - ".join(
                                [lang_file.get(repr(mode), guild) for mode in self.modes]),
                            inline=False)
        else:
            embed.add_field(name=lang_file.get("coc_game_mode", guild),
                            value=lang_file.get(repr(self.mode), guild),
                            inline=True)

        if self.state == State.FINISHED:
            winner = sorted(self.players, key=lambda player: player.rank)[0]
            embed.add_field(name=lang_file.get("coc_game_winner", guild),
                            value=f"🏆 {winner.name}",
                            inline=True)
        else:
            embed.add_field(name=lang_file.get("coc_game_players", guild),
                            value=f"`{'`, `'.join([f'{str(player.state)} {player.name}' for player in self.players])}`",
                            inline=False)

            languages = f"`{'`, `'.join(self.programming_language)}`" \
                if len(self.programming_language) >= 1 \
                else lang_file.get("coc_all_languages", guild)

            embed.add_field(name=lang_file.get("coc_game_languages", guild),
                            value=languages)

        return embed
