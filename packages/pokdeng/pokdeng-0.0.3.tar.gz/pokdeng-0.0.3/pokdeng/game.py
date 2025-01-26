from decimal import Decimal
from typing import Dict, List

from pokdeng.card import Deck
from pokdeng.cardholder import Dealer, Player
from pokdeng.exception import GameLessThan1Player, GameMoreThan16Players, GameNoDealer, GamePocketMismatch
from pokdeng.hand import Hand
from pokdeng.idgenerator import CardHolderId
from pokdeng.pocket import Pocket

class Game:
    def __init__(self, dealer: Dealer, players: List[Player], pockets: Dict[CardHolderId, Pocket], verbose: bool = False):
        if dealer is None:
            raise GameNoDealer()
        if (len(players)) < 1:
            raise GameLessThan1Player()
        if len(players) > 16:
            raise GameMoreThan16Players()
        if len({player for player in players if pockets.get(player.card_holder_id) is not None}) != len(players) or pockets.get(dealer.card_holder_id) is None:
            raise GamePocketMismatch()

        self.dealer: Dealer = dealer
        self.players: List[Player] = players
        self.pockets: Dict[CardHolderId, Pocket] = pockets

        self.round: int = 0
        self.verbose: bool = verbose

    def play(self, num_rounds: int):
        for _ in range(num_rounds):
            self.round += 1
            deck: Deck = Deck()
            bets: Dict[CardHolderId, Decimal] = {player.card_holder_id : player.place_bet(self.round, self.pockets[player.card_holder_id]) for player in self.players}
            players: List[Player] = [player for player in self.players if bets.get(player.card_holder_id) is not None]
            hands: Dict[CardHolderId, Hand] = {}

            if len(players) == 0:
                if self.verbose:
                    print(f"[round={self.round}] no players bet")
                continue

            for player in players:
                hands[player.card_holder_id] = Hand(cards = [deck.draw(), deck.draw()])
            hands[self.dealer.card_holder_id] = Hand(cards = [deck.draw(), deck.draw()])

            for player in players:
                player_hand = hands.get(player.card_holder_id)
                if player_hand.pok():
                    continue
                pocket = self.pockets.get(player.card_holder_id)
                if player.draw_card(self.round, pocket, player_hand):
                    hands[player.card_holder_id] = Hand(cards = player_hand.cards + [deck.draw()])

            dealer_pocket = self.pockets.get(self.dealer.card_holder_id)
            dealer_hand = hands.get(self.dealer.card_holder_id)

            if dealer_hand.pok():
                self.__settle_all(players, bets, hands)
                if self.verbose:
                    print(f"[round={self.round}] settled all because dealer pok")
                continue

            if self.dealer.two_fight_three(self.round, dealer_pocket, dealer_hand):
                players_with_3_cards = [player for player in players if hands.get(player.card_holder_id).num_cards() == 3]
                self.__settle_all(players_with_3_cards, bets, hands)
                hands[self.dealer.card_holder_id] = Hand(cards = dealer_hand.cards + [deck.draw()])
                players_with_2_cards = [player for player in players if hands.get(player.card_holder_id).num_cards() == 2]
                self.__settle_all(players_with_2_cards, bets, hands)
                if self.verbose:
                    print(f"[round={self.round}] settled all after two fight three then three fight two")
                continue
            
            if self.dealer.draw_card(self.round, dealer_pocket, dealer_hand):
                hands[self.dealer.card_holder_id] = Hand(cards = dealer_hand.cards + [deck.draw()])
            
            self.__settle_all(players, bets, hands)
            if self.verbose:
                print(f"[round={self.round}] settled all normally")
    
    def __settle_all(self, players: List[Player], bets: Dict[CardHolderId, Decimal], hands: Dict[CardHolderId, Hand]):
        dealer_hand = hands.get(self.dealer.card_holder_id)
        dealer_hand_deng = dealer_hand.deng()
        for player in players:
            player_hand = hands.get(player.card_holder_id)
            player_hand_deng = player_hand.deng()
            if dealer_hand > player_hand:
                self.__pay_dealer(player, bets, dealer_hand_deng)
            elif dealer_hand < player_hand:
                self.__pay_player(player, bets, player_hand_deng)
            else:
                if dealer_hand_deng > player_hand_deng:
                    self.__pay_dealer(player, bets, dealer_hand_deng - player_hand_deng)
                elif dealer_hand_deng < player_hand_deng:
                    self.__pay_player(player, bets, player_hand_deng - dealer_hand_deng)
                else:
                    pass
    
    def __pay_dealer(self, player: Player, bets: Dict[CardHolderId, Decimal], deng: int):
        bet = bets.get(player.card_holder_id)
        amount: Decimal = bet * deng

        dealer_pocket = self.pockets.get(self.dealer.card_holder_id)
        player_pocket = self.pockets.get(player.card_holder_id)
        self.__settle_amount(from_pocket = player_pocket, to_pocket = dealer_pocket, amount = amount)
    
    def __pay_player(self, player: Player, bets: Dict[CardHolderId, Decimal], deng: int):
        bet = bets.get(player.card_holder_id)
        amount: Decimal = bet * deng

        dealer_pocket = self.pockets.get(self.dealer.card_holder_id)
        player_pocket = self.pockets.get(player.card_holder_id)
        self.__settle_amount(from_pocket = dealer_pocket, to_pocket = player_pocket, amount = amount)

    def __settle_amount(self, from_pocket: Pocket, to_pocket: Pocket, amount: Decimal):
        from_pocket.subtract_amount(amount)
        to_pocket.add_amount(amount)
