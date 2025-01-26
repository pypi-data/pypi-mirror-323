from dataclasses import dataclass
from enum import Enum
from random import shuffle
from typing import List

class Suit(Enum):
    CLUB = (1, "C")
    DIAMOND = (2, "D")
    HEART = (3, "H")
    SPADE = (4, "S")

    def __init__(self, code: int, description: str):
        self.code = code
        self.description = description

class Rank(Enum):
    TWO = (2, 2, "2")
    THREE = (3, 3, "3")
    FOUR = (4, 4, "4")
    FIVE = (5, 5, "5")
    SIX = (6, 6, "6")
    SEVEN = (7, 7, "7")
    EIGHT = (8, 8, "8")
    NINE = (9, 9, "9")
    TEN = (10, 10, "T")
    JACK = (11, 10, "J")
    QUEEN = (12, 10, "Q")
    KING = (13, 10, "K")
    ACE = (14, 1, "A")

    def __init__(self, code: int, score: int, description: str):
        self.code = code
        self.score = score
        self.description = description

    def is_face(self) -> bool:
        return self in {self.JACK, self.QUEEN, self.KING}

@dataclass
class Card:
    rank: Rank
    suit: Suit

class Deck:
    def __init__(self):
        self.cards: List[Card] = [Card(rank, suit) for rank in Rank for suit in Suit]
        shuffle(self.cards)
    
    def draw(self) -> Card:
        if len(self.cards) > 0:
            return self.cards.pop()
        return None
