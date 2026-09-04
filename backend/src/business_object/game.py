import datetime


class Game:
    def __init__(
        self,
        player1,
        player2,
        game_mode,
        winner,
        description="",
        timestamp=datetime.date.today(),
        id_game: int = None,
    ):
        self.id_game = id_game
        self.player1 = player1
        self.player2 = player2
        self.game_mode = game_mode
        self.winner = winner
        self.description = description
        self.timestamp = timestamp

    def __str__(self):
        game_mode = self.game_mode
        player1 = self.player1
        player2 = self.player2
        winner = self.winner
        s = game_mode + " between " + player1.username + " and " + player2.username
        if winner is None:
            s += ". draw  "
        else:
            s += winner.username
        return s
