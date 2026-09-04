from business_object.game import Game
from business_object.player import Player

p1 = Player("Alice", 1500, "alice@truc.machin")
p2 = Player("Bob", 1500, "bob@bidule.machin")
g = Game(p1, p2, "coinflip", None)
print(g)
