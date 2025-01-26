from dataclasses import dataclass
from decimal import Decimal

from pokdeng.idgenerator import CardHolderId

@dataclass
class Pocket:
    card_holder_id: CardHolderId
    total_amount: Decimal

    def add_amount(self, amount: Decimal):
        self.total_amount += amount
    
    def subtract_amount(self, amount: Decimal):
        self.total_amount -= amount
