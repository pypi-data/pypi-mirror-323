from dataclasses import dataclass
from functools import total_ordering
from typing import List

from pokdeng.card import Card
from pokdeng.exception import HandLessThan2Cards, HandMoreThan3Cards, DuplicateCards

@dataclass
@total_ordering
class Hand:
    cards: List[Card]

    def __post_init__(self):
        if self.__have_duplicate_cards():
            raise DuplicateCards()
        if self.num_cards() < 2:
            raise HandLessThan2Cards()
        if self.num_cards() > 3:
            raise HandMoreThan3Cards()

    def __eq__(self, other):
        if not isinstance(other, Hand):
            return NotImplemented
        return (self.pok_nine(), self.pok_eight(), self.tong(), self.straight_flush(), self.straight(), self.three_yellow(), self.score()) ==\
            (other.pok_nine(), other.pok_eight(), other.tong(), other.straight_flush(), other.straight(), other.three_yellow(), other.score())

    def __gt__(self, other):
        if not isinstance(other, Hand):
            return NotImplemented
        return (self.pok_nine(), self.pok_eight(), self.tong(), self.straight_flush(), self.straight(), self.three_yellow(), self.score()) >\
            (other.pok_nine(), other.pok_eight(), other.tong(), other.straight_flush(), other.straight(), other.three_yellow(), other.score())

    def num_cards(self) -> int:
        return len(self.cards)

    def __have_duplicate_cards(self) -> bool:
        return len(set([f"{card.rank.description}{card.suit.description}" for card in self.cards])) < self.num_cards()

    def score(self) -> int:
        return sum([card.rank.score for card in self.cards]) % 10

    def __num_unique_ranks(self) -> int:
        return len(set([card.rank for card in self.cards]))
    
    def __num_unique_suits(self) -> int:
        return len(set([card.suit for card in self.cards]))
    
    def __num_faces(self) -> int:
        return len([card for card in self.cards if card.rank.is_face()])
    
    def pok(self) -> bool:
        return self.pok_eight() or self.pok_nine()

    def pok_eight(self) -> bool:
        return self.num_cards() == 2 and self.score() == 8

    def pok_nine(self) -> bool:
        return self.num_cards() == 2 and self.score() == 9
    
    def tong(self) -> bool:
        return self.num_cards() == 3 and self.__num_unique_ranks() == 1 and self.__num_unique_suits() == 3
    
    def straight_flush(self) -> bool:
        if not self.straight():
            return False
        return self.__num_unique_suits() == 1

    def straight(self) -> bool:
        if self.num_cards() != 3:
            return False
        if self.__num_unique_ranks() != 3:
            return False
        combination = "".join([rank.description for rank in sorted([card.rank for card in self.cards], key = lambda rank: rank.code)])
        return combination in {"234", "345", "456", "567", "678", "789", "89T", "9TJ", "TJQ", "JQK", "QKA"}

    def three_yellow(self) -> bool:
        return self.num_cards() == 3 and self.__num_faces() == 3 and not self.straight() and not self.tong()

    def deng(self) -> int:
        if self.num_cards() == 2:
            if self.__num_unique_suits() == 1 or self.__num_unique_ranks() == 1:
                return 2
            return 1
        if self.tong() or self.straight_flush():
            return 5
        if self.straight() or self.three_yellow():
            return 3
        if self.__num_unique_suits() == 1:
            return 3
        return 1
    
    
