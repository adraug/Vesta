import requests
from vesta.services.clash_of_code_entities import *


def game_id_from_link(link: str) -> str:
    return link.split("/")[-1]


class ClashOfCodeHelper:
    __instance = None
    BASE_ENDPOINT = "https://www.codingame.com/services/ClashOfCode/"

    def __new__(cls, *args, **kwargs):
        if ClashOfCodeHelper.__instance is None:
            ClashOfCodeHelper.__instance = super(ClashOfCodeHelper, cls).__new__(cls, *args, **kwargs)
        return ClashOfCodeHelper.__instance

    def fetch(self, game_id) -> Optional[ClashOfCodeGame]:
        """
        Retrieves a game object from the API

        :param game_id: The game id to retrieve
        :return: The game object if it exists, None otherwise
        """
        r = requests.post(f"{self.BASE_ENDPOINT}findClashByHandle", json=[
            game_id
        ])

        if r.status_code != 200:
            return None

        return ClashOfCodeGame(**r.json())

    def update(self, game: ClashOfCodeGame) -> ClashOfCodeGame:
        """
        Updates the game object with the latest information from the API

        :param game: The game object to update
        :return: The updated game object for chaining convenience
        :raises NameError: If there was an error updating the game object
        """
        r = requests.post(f"{self.BASE_ENDPOINT}findClashByHandle", json=[
            game_id_from_link(game.link)
        ])

        if r.status_code != 200:
            raise NameError("There was an error updating the game object")

        game.hydrate(**r.json())
        return game

