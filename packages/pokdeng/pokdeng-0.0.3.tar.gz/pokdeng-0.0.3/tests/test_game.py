from decimal import Decimal
from unittest import TestCase, main

from pokdeng.cardholder import Dealer, Player
from pokdeng.exception import GameLessThan1Player, GameMoreThan16Players, GameNoDealer, GamePocketMismatch
from pokdeng.game import Game
from pokdeng.pocket import Pocket

class TestGame(TestCase):

    def test_GameNoDealer(self):
        kanye = Player()
        ben = Player()

        kanye_pocket = Pocket(kanye.card_holder_id, Decimal("10"))
        ben_pocket = Pocket(ben.card_holder_id, Decimal("10"))
        pockets = {pocket.card_holder_id: pocket for pocket in [kanye_pocket, ben_pocket]}

        with self.assertRaises(GameNoDealer):
            Game(dealer = None, players = [kanye, ben], pockets = pockets)

    def test_GameLessThan1Player(self):
        anita = Dealer()
        anita_pocket = Pocket(anita.card_holder_id, Decimal("0"))
        pockets = {pocket.card_holder_id: pocket for pocket in [anita_pocket]}

        with self.assertRaises(GameLessThan1Player):
            Game(dealer = anita, players = [], pockets = pockets)

    def test_GameMoreThan16Players(self):
        players = [Player() for _ in range(17)]
        anita = Dealer()

        player_pockets = [Pocket(player.card_holder_id, Decimal("10")) for player in players]
        anita_pocket = Pocket(anita.card_holder_id, Decimal("0"))
        pockets = {pocket.card_holder_id: pocket for pocket in player_pockets + [anita_pocket]}

        with self.assertRaises(GameMoreThan16Players):
            Game(dealer = anita, players = players, pockets = pockets)

    def test_GamePocketMismatch(self):
        kanye = Player()
        ben = Player()
        anita = Dealer()

        kanye_pocket = Pocket(kanye.card_holder_id, Decimal("10"))
        ben_pocket = Pocket(ben.card_holder_id, Decimal("10"))        
        anita_pocket = Pocket(anita.card_holder_id, Decimal("0"))

        with self.assertRaises(GamePocketMismatch):
            pockets = {pocket.card_holder_id: pocket for pocket in [kanye_pocket, ben_pocket]}
            Game(dealer = anita, players = [kanye, ben], pockets = pockets)

        with self.assertRaises(GamePocketMismatch):
            pockets = {pocket.card_holder_id: pocket for pocket in [kanye_pocket, anita_pocket]}
            Game(dealer = anita, players = [kanye, ben], pockets = pockets)
    
    def test_play(self):
        kanye = Player()
        ben = Player()
        anita = Dealer()

        kanye_pocket = Pocket(kanye.card_holder_id, Decimal("10"))
        ben_pocket = Pocket(ben.card_holder_id, Decimal("10"))        
        anita_pocket = Pocket(anita.card_holder_id, Decimal("0"))
        pockets = {pocket.card_holder_id: pocket for pocket in [kanye_pocket, ben_pocket, anita_pocket]}
        
        game = Game(dealer = anita, players = [kanye, ben], pockets = pockets, verbose = True)
        game.play(10)

        total_amount_after_play: Decimal = sum([pocket.total_amount for pocket in pockets.values()])
        self.assertEqual(total_amount_after_play, Decimal("20"))

if __name__ == '__main__':
    main()
