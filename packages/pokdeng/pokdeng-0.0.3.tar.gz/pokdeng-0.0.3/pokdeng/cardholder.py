from abc import ABC, abstractmethod
from decimal import Decimal

from pokdeng.hand import Hand
from pokdeng.idgenerator import CardHolderId
from pokdeng.pocket import Pocket

class CardHolder(ABC):
    def __init__(self, card_holder_id: CardHolderId):
        self.card_holder_id: CardHolderId = card_holder_id

    @abstractmethod
    def draw_card(self, round: int, pocket: Pocket, hand: Hand) -> bool:
        pass

class Dealer(CardHolder):
    def __init__(self, card_holder_id: CardHolderId = None):
        if card_holder_id is None:
            card_holder_id = CardHolderId()
        super().__init__(card_holder_id)

    def draw_card(self, round: int, pocket: Pocket, hand: Hand) -> bool:
        return hand.score() < 5

    def two_fight_three(self, round: int, pocket: Pocket, hand: Hand) -> bool:
        return hand.score() > 5

class Player(CardHolder):
    def __init__(self, card_holder_id: CardHolderId = None):
        if card_holder_id is None:
            card_holder_id = CardHolderId()
        super().__init__(card_holder_id)

    def draw_card(self, round: int, pocket: Pocket, hand: Hand) -> bool:
        return hand.score() < 5
    
    def place_bet(self, round: int, pocket: Pocket) -> Decimal:
        bet = Decimal("1")
        if pocket.total_amount - bet > Decimal("0"):
            return bet
        return None
