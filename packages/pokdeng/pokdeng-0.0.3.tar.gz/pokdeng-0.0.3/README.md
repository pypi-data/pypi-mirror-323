# pokdeng

[pokdeng](https://pypi.org/project/pokdeng/) is a Python package for simulating rounds of pokdeng games!

[Visit repository on Github](https://github.com/papillonbee/pokdeng)

---

## Quick Guide
Create player ```Kanye``` where he will
- place bet amount = 2 if his pocket has a minimum balance of 3 after deducting the bet amount
- draw the third card if his two cards on hand are not two deng or score less than 4
```python
from pokdeng.cardholder import Dealer, Player
from pokdeng.hand import Hand
from pokdeng.game import Game
from pokdeng.pocket import Pocket
from decimal import Decimal

class Kanye(Player):
    def place_bet(self, round: int, pocket: Pocket) -> Decimal:
        bet = Decimal("2")
        if pocket.total_amount - bet >= Decimal("3"):
            return bet
        return None
    def draw_card(self, round: int, pocket: Pocket, hand: Hand) -> bool:
        return hand.deng() != 2 or hand.score() < 4
```

```python
kanye = Kanye()
```

Create player ```Ben``` where he will
- place bet amount = 1 if his pocket has a minimum balance of 0 after deducting the bet amount
- draw the third card if his two cards on hand score lesss than 5

```python
ben = Player()
```

Create dealer ```Anita``` where she will
- fight her two cards on hand with three cards on other player's hands if two deng and score more than 4
- draw the third card if her two cards on hand score less than 3
```python
class Anita(Dealer):
    def two_fight_three(self, round: int, pocket: Pocket, hand: Hand) -> bool:
        return hand.deng() == 2 and hand.score() > 4
    def draw_card(self, round: int, pocket: Pocket, hand: Hand) -> bool:
        return hand.score() < 3
```

```python
anita = Anita()
```

Create dealer ```Dixon``` where he will
- fight his two cards on hand with three cards on other player's hands if score more than 5
- draw the third card if his two cards on hand score less than 5

```python
dixon = Dealer()
```

Create pocket for each dealer/player with some amount where dealer's pocket usually starts with 0 amount while player's pocket starts with positive amount
```python
kanye_pocket = Pocket(kanye.card_holder_id, Decimal(10))
ben_pocket = Pocket(ben.card_holder_id, Decimal(10))
anita_pocket = Pocket(anita.card_holder_id, Decimal(0))
```

Create a collection of pockets by dealer/player
```python
pockets = {pocket.card_holder_id: pocket for pocket in [kanye_pocket, ben_pocket, anita_pocket]}
```

Create a game of 1 dealer, a list of players, and a collection of pockets by dealer/player
```python
game = Game(dealer = anita, players = [kanye, ben], pockets = pockets)
```

Play the game for 200 rounds
```python
game.play(200)
```

Check total amount in each pocket afterwards
```python
[(card_holder_id.value, pocket.total_amount) for card_holder_id, pocket in pockets.items()]
```

Pokdeng is a zero sum game, meaning the total amount of every pockets after each play always sums to the initial total amount of every pockets

---

## Understanding hand comparison rules

```python
from pokdeng.card import Card, Rank, Suit
```

Case #1: JQK same suit (straight flush) ties with TJQ same suit (straight flush)
```python
hand1 = Hand(cards = [Card(Rank.JACK, Suit.CLUB), Card(Rank.KING, Suit.CLUB), Card(Rank.QUEEN, Suit.CLUB)])
hand2 = Hand(cards = [Card(Rank.TEN, Suit.HEART), Card(Rank.JACK, Suit.HEART), Card(Rank.QUEEN, Suit.HEART)])
print(hand1.straight_flush(), hand2.straight_flush()) # True True
print(hand1.score(), hand2.score()) # 0 0
print(hand1.deng(), hand2.deng()) # 5 5
print(hand1 == hand2) # True
```
Case #2: 555 (tong) wins 567 same suit (straight flush)
```python
hand1 = Hand(cards = [Card(Rank.FIVE, Suit.CLUB), Card(Rank.FIVE, Suit.SPADE), Card(Rank.FIVE, Suit.DIAMOND)])
hand2 = Hand(cards = [Card(Rank.FIVE, Suit.HEART), Card(Rank.SIX, Suit.HEART), Card(Rank.SEVEN, Suit.HEART)])
print(hand1.tong(), hand2.tong()) # True False
print(hand1.straight_flush(), hand2.straight_flush()) # False True
print(hand1 > hand2) # True
```
Case #3: KKK (tong) loses 222 (tong)
```python
hand1 = Hand(cards = [Card(Rank.KING, Suit.CLUB), Card(Rank.KING, Suit.SPADE), Card(Rank.KING, Suit.DIAMOND)])
hand2 = Hand(cards = [Card(Rank.TWO, Suit.CLUB), Card(Rank.TWO, Suit.SPADE), Card(Rank.TWO, Suit.HEART)])
print(hand1.tong(), hand2.tong()) # True True
print(hand1.score(), hand2.score()) # 0 6
print(hand1 < hand2) # True
```
Case #4: 345 different suit (straight) wins JJQ (three yellow)
```python
hand1 = Hand(cards = [Card(Rank.THREE, Suit.CLUB), Card(Rank.FOUR, Suit.SPADE), Card(Rank.FIVE, Suit.CLUB)])
hand2 = Hand(cards = [Card(Rank.JACK, Suit.CLUB), Card(Rank.JACK, Suit.SPADE), Card(Rank.QUEEN, Suit.HEART)])
print(hand1.straight(), hand2.straight()) # True False
print(hand1.three_yellow(), hand2.three_yellow()) # False True
print(hand1 > hand2) # True
```
Case #5: KA2 same suit (normal 3 3 deng) loses JJQ (three yellow)
```python
hand1 = Hand(cards = [Card(Rank.KING, Suit.CLUB), Card(Rank.ACE, Suit.CLUB), Card(Rank.TWO, Suit.CLUB)])
hand2 = Hand(cards = [Card(Rank.JACK, Suit.CLUB), Card(Rank.JACK, Suit.SPADE), Card(Rank.QUEEN, Suit.HEART)])
print(hand1.three_yellow(), hand2.three_yellow()) # False True
print(hand1 < hand2) # True
```
Case #6: JQK same suit (straight flush) wins 234 different suit (straight)
```python
hand1 = Hand(cards = [Card(Rank.JACK, Suit.CLUB), Card(Rank.QUEEN, Suit.CLUB), Card(Rank.KING, Suit.CLUB)])
hand2 = Hand(cards = [Card(Rank.TWO, Suit.CLUB), Card(Rank.THREE, Suit.SPADE), Card(Rank.FOUR, Suit.HEART)])
print(hand1.straight_flush(), hand2.straight_flush()) # True False
print(hand1.straight(), hand2.straight()) # True True
print(hand1 > hand2) # True
```
Case #7: KA2 same suit (normal 3 3 deng) loses A25 different suit (normal 8 1 deng)
```python
hand1 = Hand(cards = [Card(Rank.KING, Suit.CLUB), Card(Rank.ACE, Suit.CLUB), Card(Rank.TWO, Suit.CLUB)])
hand2 = Hand(cards = [Card(Rank.ACE, Suit.CLUB), Card(Rank.TWO, Suit.SPADE), Card(Rank.FIVE, Suit.HEART)])
print(hand1.score(), hand2.score()) # 3 8
print(hand1 < hand2) # True
```
Case #8: A2 same suit (normal 3 2 deng) ties with A2T same suit (normal 3 3 deng)
```python
hand1 = Hand(cards = [Card(Rank.ACE, Suit.SPADE), Card(Rank.TWO, Suit.SPADE)])
hand2 = Hand(cards = [Card(Rank.ACE, Suit.HEART), Card(Rank.TEN, Suit.HEART), Card(Rank.TWO, Suit.HEART)])
print(hand1.score(), hand2.score()) # 3 3
print(hand1.deng(), hand2.deng()) # 2 3
print(hand1 == hand2) # True
```
Case #9: A2 different suit (normal 1 deng) wins ATJ different suit (normal 1 deng)
```python
hand1 = Hand(cards = [Card(Rank.ACE, Suit.SPADE), Card(Rank.TWO, Suit.HEART)])
hand2 = Hand(cards = [Card(Rank.ACE, Suit.HEART), Card(Rank.TEN, Suit.HEART), Card(Rank.JACK, Suit.DIAMOND)])
print(hand1.score(), hand2.score()) # 3 1
print(hand1 > hand2) # True
```
Case #10: 45 different suit (pok nine 1 deng) wins 99 (pok eight 2 deng)
```python
hand1 = Hand(cards = [Card(Rank.FIVE, Suit.SPADE), Card(Rank.FOUR, Suit.CLUB)])
hand2 = Hand(cards = [Card(Rank.NINE, Suit.SPADE), Card(Rank.NINE, Suit.DIAMOND)])
print(hand1.pok_nine(), hand2.pok_nine()) # True False
print(hand1.pok_eight(), hand2.pok_eight()) # False True
print(hand1 > hand2) # True
```
Case #11: A67 same suit (normal 4 3 deng) ties with 22 (normal 4 2 deng)
```python
hand1 = Hand(cards = [Card(Rank.ACE, Suit.CLUB), Card(Rank.SIX, Suit.CLUB), Card(Rank.SEVEN, Suit.CLUB)])
hand2 = Hand(cards = [Card(Rank.TWO, Suit.SPADE), Card(Rank.TWO, Suit.HEART)])
print(hand1.score(), hand2.score()) # 4 4
print(hand1.deng(), hand2.deng()) # 3 2
print(hand1 == hand2) # True
```
More cases under ```tests/test_hand.py```
