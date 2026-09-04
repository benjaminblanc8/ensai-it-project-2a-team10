from business_object.game_moding.game_mode import CoinFlipMode, DiceMode


class GameModeFactory:
    def get_mode(cls, game_mode):
        """
        Returns the corresponding GameMode object.
        Args:
            game_mode (str): The identifier of the game mode (e.g., 'coinflip', 'dice').
        Returns:
            GameMode: An instance of a class implementing GameMode.
        Raises:
            ValueError: If the requested game_mode is not supported.
        """
        if game_mode == "dice":
            return DiceMode()
        elif game_mode == "coinflip":
            return CoinFlipMode()
        else:
            raise ValueError("unknown game mode")
