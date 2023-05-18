import requests
from vesta.services.clash_of_code_entities import *


class ClashOfCodeHelper:
    BASE_ENDPOINT = "https://www.codingame.com/services/ClashOfCode/"

    def __init__(self):
        pass

    def fetch(self, game_id) -> Optional[ClashOfCodeGame]:
        """
        Retrieves a game object from the API

        :param game_id: The game id to retrieve
        :return: The game object if it exists, None otherwise
        """
        r = requests.post(f"{self.BASE_ENDPOINT}findClashByHandle", json=[
            game_id
        ]).json()

        if r["id"] == 502 or "Clash not found" in r["message"]:
            return None

        return ClashOfCodeGame(**r)

    def update(self, game: ClashOfCodeGame) -> ClashOfCodeGame:
        """
        Updates the game object with the latest information from the API

        :param game: The game object to update
        :return: The updated game object for chaining convenience
        """
        r = requests.post(f"{self.BASE_ENDPOINT}findClashByHandle", json=[
            game.link.split("/")[-1]
        ]).json()

        if r["id"] == 502 or "Clash not found" in r["message"]:
            raise NameError("Clash does not exist anymore")

        game.hydrate(**r)
        return game