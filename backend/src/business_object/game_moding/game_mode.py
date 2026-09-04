import secrets
from abc import ABC, abstractmethod

from business_object.game import Game


class GameMode(ABC):
    @abstractmethod
    def play(self, p1, p2, **kwargs):
        pass


class DiceMode(GameMode):
    def __init__(self):
        self.game_mode = "dice"

    def play(self, p1, p2):
        d1 = secrets.choice(range(1, 7))
        d2 = secrets.choice(range(1, 7))
        if d1 > d2:
            winner = p1
        elif d1 < d2:
            winner = p2
        else:
            winner = None
        return Game(p1, p2, self.game_mode, winner)


class CoinFlipMode(GameMode):
    def __init__(self):
        self.game_mode = "coinflip"

    def play(self, p1, p2, choice="heads"):
        result = secrets.choice(["heads", "tails"])
        winner = p1 if result == choice else p2
        return Game(p1, p2, self.game_mode, winner)
