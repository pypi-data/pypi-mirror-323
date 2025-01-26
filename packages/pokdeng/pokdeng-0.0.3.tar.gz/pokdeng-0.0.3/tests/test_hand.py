from unittest import TestCase, main

from pokdeng.card import Card, Rank, Suit
from pokdeng.exception import DuplicateCards, HandLessThan2Cards, HandMoreThan3Cards
from pokdeng.hand import Hand

class TestHand(TestCase):

    def test_DuplicateCards(self):
        with self.assertRaises(DuplicateCards):
            Hand(cards = [Card(Rank.ACE, Suit.SPADE), Card(Rank.ACE, Suit.SPADE)])

    def test_HandLessThan2Cards(self):
        with self.assertRaises(HandLessThan2Cards):
            Hand(cards = [Card(Rank.ACE, Suit.SPADE)])
    
    def test_HandMoreThan3Cards(self):
        with self.assertRaises(HandMoreThan3Cards):
            Hand(cards = [Card(Rank.NINE, Suit.CLUB), Card(Rank.NINE, Suit.DIAMOND), Card(Rank.NINE, Suit.HEART), Card(Rank.NINE, Suit.SPADE)])

    def test_pok_nine(self):
        # A8 is pok nine
        hand = Hand(cards = [Card(Rank.ACE, Suit.CLUB), Card(Rank.EIGHT, Suit.HEART)])
        self.assertTrue(hand.pok_nine())

        # A7 is pok eight
        hand = Hand(cards = [Card(Rank.ACE, Suit.CLUB), Card(Rank.SEVEN, Suit.HEART)])
        self.assertFalse(hand.pok_nine())

        # A26 is normal 9
        hand = Hand(cards = [Card(Rank.ACE, Suit.CLUB), Card(Rank.TWO, Suit.SPADE), Card(Rank.SIX, Suit.HEART)])
        self.assertFalse(hand.pok_nine())

    def test_pok_eight(self):
        # A7 is pok eight
        hand = Hand(cards = [Card(Rank.ACE, Suit.CLUB), Card(Rank.SEVEN, Suit.HEART)])
        self.assertTrue(hand.pok_eight())

        # A8 is pok nine
        hand = Hand(cards = [Card(Rank.ACE, Suit.CLUB), Card(Rank.EIGHT, Suit.HEART)])
        self.assertFalse(hand.pok_eight())

        # AA6 is nornal 8
        hand = Hand(cards = [Card(Rank.ACE, Suit.CLUB), Card(Rank.ACE, Suit.SPADE), Card(Rank.SIX, Suit.HEART)])
        self.assertFalse(hand.pok_eight())

    def test_tong(self):
        # 999 is tong
        hand = Hand(cards = [Card(Rank.NINE, Suit.CLUB), Card(Rank.NINE, Suit.DIAMOND), Card(Rank.NINE, Suit.HEART)])
        self.assertTrue(hand.tong())

        # 99T is normal 8
        hand = Hand(cards = [Card(Rank.NINE, Suit.CLUB), Card(Rank.NINE, Suit.DIAMOND), Card(Rank.TEN, Suit.HEART)])
        self.assertFalse(hand.tong())

        # JJJ is tong
        hand = Hand(cards = [Card(Rank.JACK, Suit.CLUB), Card(Rank.JACK, Suit.DIAMOND), Card(Rank.JACK, Suit.HEART)])
        self.assertTrue(hand.tong())
    
    def test_straight_flush(self):
        # 234 same suit is straight flush
        hand = Hand(cards = [Card(Rank.TWO, Suit.CLUB), Card(Rank.THREE, Suit.CLUB), Card(Rank.FOUR, Suit.CLUB)])
        self.assertTrue(hand.straight_flush())

        # JQK same suit is straight flush
        hand = Hand(cards = [Card(Rank.JACK, Suit.CLUB), Card(Rank.QUEEN, Suit.CLUB), Card(Rank.KING, Suit.CLUB)])
        self.assertTrue(hand.straight_flush())

        # QKA same suit is straight flush
        hand = Hand(cards = [Card(Rank.QUEEN, Suit.CLUB), Card(Rank.KING, Suit.CLUB), Card(Rank.ACE, Suit.CLUB)])
        self.assertTrue(hand.straight_flush())

        # KA2 same suit is normal 3 3 deng
        hand = Hand(cards = [Card(Rank.KING, Suit.CLUB), Card(Rank.ACE, Suit.CLUB), Card(Rank.TWO, Suit.CLUB)])
        self.assertFalse(hand.straight_flush())

        # A23 same suit is normal 6 3 deng
        hand = Hand(cards = [Card(Rank.ACE, Suit.CLUB), Card(Rank.TWO, Suit.CLUB), Card(Rank.THREE, Suit.CLUB)])
        self.assertFalse(hand.straight_flush())

        # 567 different suit is straight
        hand = Hand(cards = [Card(Rank.FIVE, Suit.CLUB), Card(Rank.SIX, Suit.CLUB), Card(Rank.SEVEN, Suit.HEART)])
        self.assertFalse(hand.straight_flush())

        # 45 same suit is pok nine
        hand = Hand(cards = [Card(Rank.FOUR, Suit.CLUB), Card(Rank.FIVE, Suit.CLUB)])
        self.assertFalse(hand.straight_flush())

    def test_straight(self):
        # 234 different suit is straight
        hand = Hand(cards = [Card(Rank.TWO, Suit.CLUB), Card(Rank.THREE, Suit.CLUB), Card(Rank.FOUR, Suit.CLUB)])
        self.assertTrue(hand.straight())

        # JQK same suit is both straight and straight flush
        hand = Hand(cards = [Card(Rank.JACK, Suit.CLUB), Card(Rank.QUEEN, Suit.CLUB), Card(Rank.KING, Suit.CLUB)])
        self.assertTrue(hand.straight())

        # QKA same suit is both straight and straight flush
        hand = Hand(cards = [Card(Rank.QUEEN, Suit.CLUB), Card(Rank.KING, Suit.CLUB), Card(Rank.ACE, Suit.CLUB)])
        self.assertTrue(hand.straight())

        # KA2 same suit is normal 2 3 deng
        hand = Hand(cards = [Card(Rank.KING, Suit.CLUB), Card(Rank.ACE, Suit.CLUB), Card(Rank.TWO, Suit.CLUB)])
        self.assertFalse(hand.straight())

        # A23 same suit is normal 6 3 deng
        hand = Hand(cards = [Card(Rank.ACE, Suit.CLUB), Card(Rank.TWO, Suit.CLUB), Card(Rank.THREE, Suit.CLUB)])
        self.assertFalse(hand.straight())

        # 567 different suit is straight
        hand = Hand(cards = [Card(Rank.FIVE, Suit.CLUB), Card(Rank.SIX, Suit.CLUB), Card(Rank.SEVEN, Suit.HEART)])
        self.assertTrue(hand.straight())

        # 45 same suit is pok nine
        hand = Hand(cards = [Card(Rank.FOUR, Suit.CLUB), Card(Rank.FIVE, Suit.CLUB)])
        self.assertFalse(hand.straight())

    def test_three_yellow(self):
        # JJQ different suit is three yellow
        hand = Hand(cards = [Card(Rank.JACK, Suit.CLUB), Card(Rank.JACK, Suit.DIAMOND), Card(Rank.QUEEN, Suit.HEART)])
        self.assertTrue(hand.three_yellow())

        # JJJ is tong
        hand = Hand(cards = [Card(Rank.JACK, Suit.CLUB), Card(Rank.JACK, Suit.DIAMOND), Card(Rank.JACK, Suit.HEART)])
        self.assertFalse(hand.three_yellow())

        # JJA is normal 1
        hand = Hand(cards = [Card(Rank.JACK, Suit.CLUB), Card(Rank.JACK, Suit.DIAMOND), Card(Rank.ACE, Suit.HEART)])
        self.assertFalse(hand.three_yellow())
    
    def test_compare_hand(self):
        # Case #1: JQK same suit (straight flush) ties with TJQ same suit (straight flush)
        hand1 = Hand(cards = [Card(Rank.JACK, Suit.CLUB), Card(Rank.KING, Suit.CLUB), Card(Rank.QUEEN, Suit.CLUB)])
        hand2 = Hand(cards = [Card(Rank.TEN, Suit.HEART), Card(Rank.JACK, Suit.HEART), Card(Rank.QUEEN, Suit.HEART)])
        self.assertTrue(hand1 == hand2)
        self.assertEqual(hand1.score(), 0)
        self.assertEqual(hand2.score(), 0)
        self.assertEqual(hand1.deng(), 5)
        self.assertEqual(hand2.deng(), 5)

        # Case #2: 555 (tong) wins 567 same suit (straight flush)
        hand1 = Hand(cards = [Card(Rank.FIVE, Suit.CLUB), Card(Rank.FIVE, Suit.SPADE), Card(Rank.FIVE, Suit.DIAMOND)])
        hand2 = Hand(cards = [Card(Rank.FIVE, Suit.HEART), Card(Rank.SIX, Suit.HEART), Card(Rank.SEVEN, Suit.HEART)])
        self.assertTrue(hand1 > hand2)

        # Case #3: KKK (tong) loses 222 (tong)
        hand1 = Hand(cards = [Card(Rank.KING, Suit.CLUB), Card(Rank.KING, Suit.SPADE), Card(Rank.KING, Suit.DIAMOND)])
        hand2 = Hand(cards = [Card(Rank.TWO, Suit.CLUB), Card(Rank.TWO, Suit.SPADE), Card(Rank.TWO, Suit.HEART)])
        self.assertTrue(hand1 < hand2)

        # Case #4: 345 different suit (straight) wins JJQ (three yellow)
        hand1 = Hand(cards = [Card(Rank.THREE, Suit.CLUB), Card(Rank.FOUR, Suit.SPADE), Card(Rank.FIVE, Suit.CLUB)])
        hand2 = Hand(cards = [Card(Rank.JACK, Suit.CLUB), Card(Rank.JACK, Suit.SPADE), Card(Rank.QUEEN, Suit.HEART)])
        self.assertTrue(hand1 > hand2)

        # Case #5: KA2 same suit (normal 3 3 deng) loses JJQ (three yellow)
        hand1 = Hand(cards = [Card(Rank.KING, Suit.CLUB), Card(Rank.ACE, Suit.CLUB), Card(Rank.TWO, Suit.CLUB)])
        hand2 = Hand(cards = [Card(Rank.JACK, Suit.CLUB), Card(Rank.JACK, Suit.SPADE), Card(Rank.QUEEN, Suit.HEART)])
        self.assertTrue(hand1 < hand2)

        # Case #6: JQK same suit (straight flush) wins 234 different suit (straight)
        hand1 = Hand(cards = [Card(Rank.JACK, Suit.SPADE), Card(Rank.KING, Suit.SPADE), Card(Rank.QUEEN, Suit.SPADE)])
        hand2 = Hand(cards = [Card(Rank.TWO, Suit.SPADE), Card(Rank.THREE, Suit.SPADE), Card(Rank.FOUR, Suit.HEART)])
        self.assertTrue(hand1 > hand2)

        # Case #7: KA2 same suit (normal 3 3 deng) loses A25 different suit (normal 8 1 deng)
        hand1 = Hand(cards = [Card(Rank.KING, Suit.CLUB), Card(Rank.ACE, Suit.CLUB), Card(Rank.TWO, Suit.CLUB)])
        hand2 = Hand(cards = [Card(Rank.ACE, Suit.CLUB), Card(Rank.TWO, Suit.SPADE), Card(Rank.FIVE, Suit.HEART)])
        self.assertTrue(hand1 < hand2)

        # Case #8: A2 same suit (normal 3 2 deng) ties with A2T same suit (normal 3 3 deng)
        hand1 = Hand(cards = [Card(Rank.ACE, Suit.SPADE), Card(Rank.TWO, Suit.SPADE)])
        hand2 = Hand(cards = [Card(Rank.ACE, Suit.HEART), Card(Rank.TEN, Suit.HEART), Card(Rank.TWO, Suit.HEART)])
        self.assertTrue(hand1 == hand2)
        self.assertEqual(hand1.deng(), 2)
        self.assertEqual(hand2.deng(), 3)

        # Case #9: A2 different suit (normal 3 1 deng) wins ATJ different suit (normal 1 1 deng)
        hand1 = Hand(cards = [Card(Rank.ACE, Suit.SPADE), Card(Rank.TWO, Suit.HEART)])
        hand2 = Hand(cards = [Card(Rank.ACE, Suit.HEART), Card(Rank.TEN, Suit.HEART), Card(Rank.JACK, Suit.DIAMOND)])
        self.assertTrue(hand1 > hand2)

        # Case #10: 45 different suit (pok nine 1 deng) wins 99 (pok eight 2 deng)
        hand1 = Hand(cards = [Card(Rank.FIVE, Suit.SPADE), Card(Rank.FOUR, Suit.CLUB)])
        hand2 = Hand(cards = [Card(Rank.NINE, Suit.SPADE), Card(Rank.NINE, Suit.DIAMOND)])
        self.assertTrue(hand1 > hand2)

        # Case #11: A67 same suit (normal 4 3 deng) ties with 22 (normal 4 2 deng)
        hand1 = Hand(cards = [Card(Rank.ACE, Suit.CLUB), Card(Rank.SIX, Suit.CLUB), Card(Rank.SEVEN, Suit.CLUB)])
        hand2 = Hand(cards = [Card(Rank.TWO, Suit.SPADE), Card(Rank.TWO, Suit.HEART)])
        self.assertTrue(hand1 == hand2)
        self.assertEqual(hand1.deng(), 3)
        self.assertEqual(hand2.deng(), 2)

        # Case #12: JJK different suit (three yellow) wins A34 same suit (normal 8 3 deng)
        hand1 = Hand(cards = [Card(Rank.JACK, Suit.SPADE), Card(Rank.KING, Suit.SPADE), Card(Rank.JACK, Suit.HEART)])
        hand2 = Hand(cards = [Card(Rank.ACE, Suit.SPADE), Card(Rank.THREE, Suit.SPADE), Card(Rank.FOUR, Suit.SPADE)])
        self.assertTrue(hand1 > hand2)

        # Case #13: A34 same suit (normal 8 3 deng) ties with A34 different suit (normal 8 1 deng)
        hand1 = Hand(cards = [Card(Rank.ACE, Suit.SPADE), Card(Rank.THREE, Suit.SPADE), Card(Rank.FOUR, Suit.SPADE)])
        hand2 = Hand(cards = [Card(Rank.ACE, Suit.HEART), Card(Rank.THREE, Suit.HEART), Card(Rank.FOUR, Suit.DIAMOND)])
        self.assertTrue(hand1 == hand2)
        self.assertEqual(hand1.deng(), 3)
        self.assertEqual(hand2.deng(), 1)

        # Case #14: A34 different suit (normal 8 1 deng) ties with A34 different suit (normal 8 1 deng)
        hand1 = Hand(cards = [Card(Rank.ACE, Suit.SPADE), Card(Rank.THREE, Suit.SPADE), Card(Rank.FOUR, Suit.CLUB)])
        hand2 = Hand(cards = [Card(Rank.ACE, Suit.HEART), Card(Rank.THREE, Suit.HEART), Card(Rank.FOUR, Suit.DIAMOND)])
        self.assertTrue(hand1 == hand2)
        self.assertEqual(hand1.deng(), 1)
        self.assertEqual(hand2.deng(), 1)

        # Case #15: A3 same suit (normal 4 2 deng) ties with AA2 different suit (normal 4 1 deng)
        hand1 = Hand(cards = [Card(Rank.ACE, Suit.CLUB), Card(Rank.THREE, Suit.CLUB)])
        hand2 = Hand(cards = [Card(Rank.ACE, Suit.HEART), Card(Rank.ACE, Suit.SPADE), Card(Rank.TWO, Suit.DIAMOND)])
        self.assertTrue(hand1 == hand2)
        self.assertEqual(hand1.deng(), 2)
        self.assertEqual(hand2.deng(), 1)

        # Case #16: A3 different suit (normal 4 1 deng) ties with AA2 different suit (normal 4 1 deng)
        hand1 = Hand(cards = [Card(Rank.ACE, Suit.SPADE), Card(Rank.THREE, Suit.DIAMOND)])
        hand2 = Hand(cards = [Card(Rank.ACE, Suit.HEART), Card(Rank.ACE, Suit.CLUB), Card(Rank.TWO, Suit.DIAMOND)])
        self.assertTrue(hand1 == hand2)
        self.assertEqual(hand1.deng(), 1)
        self.assertEqual(hand2.deng(), 1)

        # Case #17: A2 same suit (normal 3 2 deng) ties with A2T same suit (normal 3 3 deng)
        hand1 = Hand(cards = [Card(Rank.ACE, Suit.SPADE), Card(Rank.TWO, Suit.SPADE)])
        hand2 = Hand(cards = [Card(Rank.ACE, Suit.HEART), Card(Rank.TEN, Suit.HEART), Card(Rank.TWO, Suit.HEART)])
        self.assertTrue(hand1 == hand2)
        self.assertEqual(hand1.deng(), 2)
        self.assertEqual(hand2.deng(), 3)

        # Case #18: A2 different suit (normal 3 1 deng) wins ATJ different suit (normal 1 1 deng)
        hand1 = Hand(cards = [Card(Rank.ACE, Suit.SPADE), Card(Rank.TWO, Suit.HEART)])
        hand2 = Hand(cards = [Card(Rank.ACE, Suit.HEART), Card(Rank.TEN, Suit.HEART), Card(Rank.JACK, Suit.DIAMOND)])
        self.assertTrue(hand1 > hand2)

        # Case #19: 45 different suit (pok nine 1 deng) wins 99 diferrent suit (pok eight 2 deng)
        hand1 = Hand(cards = [Card(Rank.FIVE, Suit.SPADE), Card(Rank.FOUR, Suit.CLUB)])
        hand2 = Hand(cards = [Card(Rank.NINE, Suit.SPADE), Card(Rank.NINE, Suit.DIAMOND)])
        self.assertTrue(hand1 > hand2)

        # Case #20: A8 same suit (pok nine 2 deng) ties with A8 different suit (pok nine 1 deng)
        hand1 = Hand(cards = [Card(Rank.ACE, Suit.CLUB), Card(Rank.EIGHT, Suit.CLUB)])
        hand2 = Hand(cards = [Card(Rank.ACE, Suit.CLUB), Card(Rank.EIGHT, Suit.SPADE)])
        self.assertTrue(hand1 == hand2)
        self.assertEqual(hand1.deng(), 2)
        self.assertEqual(hand2.deng(), 1)

        # Case #21: A8 different suit (pok nine 1 deng) wins A7 same suit (pok eight 2 deng)
        hand1 = Hand(cards = [Card(Rank.ACE, Suit.CLUB), Card(Rank.EIGHT, Suit.SPADE)])
        hand2 = Hand(cards = [Card(Rank.ACE, Suit.CLUB), Card(Rank.SEVEN, Suit.CLUB)])
        self.assertTrue(hand1 > hand2)

        # Case #22: A8 different suit (pok nine 1 deng) ties with 27 different suit (pok nine 1 deng)
        hand1 = Hand(cards = [Card(Rank.ACE, Suit.CLUB), Card(Rank.EIGHT, Suit.SPADE)])
        hand2 = Hand(cards = [Card(Rank.TWO, Suit.CLUB), Card(Rank.SEVEN, Suit.HEART)])
        self.assertTrue(hand1 == hand2)
        self.assertEqual(hand1.deng(), 1)
        self.assertEqual(hand2.deng(), 1)

        # Case #23: A7 different suit (pok eight 1 deng) wins 234 different suit (normal 9 1 deng)
        hand1 = Hand(cards = [Card(Rank.ACE, Suit.CLUB), Card(Rank.SEVEN, Suit.SPADE)])
        hand2 = Hand(cards = [Card(Rank.TWO, Suit.CLUB), Card(Rank.THREE, Suit.HEART), Card(Rank.FOUR, Suit.DIAMOND)])
        self.assertTrue(hand1 > hand2)

        # Case #24: 234 different suit (straight) wins 345 different suit (straight)
        hand1 = Hand(cards = [Card(Rank.TWO, Suit.CLUB), Card(Rank.THREE, Suit.HEART), Card(Rank.FOUR, Suit.DIAMOND)])
        hand2 = Hand(cards = [Card(Rank.THREE, Suit.CLUB), Card(Rank.FOUR, Suit.HEART), Card(Rank.FIVE, Suit.DIAMOND)])
        self.assertTrue(hand1 > hand2)

        # Case #25: JQK different suit (straight) loses JQK same suit (straight flush)
        hand1 = Hand(cards = [Card(Rank.JACK, Suit.CLUB), Card(Rank.KING, Suit.HEART), Card(Rank.QUEEN, Suit.DIAMOND)])
        hand2 = Hand(cards = [Card(Rank.JACK, Suit.SPADE), Card(Rank.KING, Suit.SPADE), Card(Rank.QUEEN, Suit.SPADE)])
        self.assertTrue(hand1 < hand2)

        # Case #26: JQK same suit (straight flush) loses 234 same suit (straight flush)
        hand1 = Hand(cards = [Card(Rank.JACK, Suit.SPADE), Card(Rank.KING, Suit.SPADE), Card(Rank.QUEEN, Suit.SPADE)])
        hand2 = Hand(cards = [Card(Rank.TWO, Suit.SPADE), Card(Rank.THREE, Suit.SPADE), Card(Rank.FOUR, Suit.SPADE)])
        self.assertTrue(hand1 < hand2)
    
    def test_deng(self):
        # 2 cards same suit is 2 deng
        hand = Hand(cards = [Card(Rank.ACE, Suit.SPADE), Card(Rank.TWO, Suit.SPADE)])
        self.assertEqual(hand.deng(), 2)

        # a pair is 2 deng
        hand = Hand(cards = [Card(Rank.ACE, Suit.SPADE), Card(Rank.ACE, Suit.CLUB)])
        self.assertEqual(hand.deng(), 2)

        # 2 cards different suit is 1 deng
        hand = Hand(cards = [Card(Rank.ACE, Suit.SPADE), Card(Rank.TWO, Suit.CLUB)])
        self.assertEqual(hand.deng(), 1)

        # tong is 5 deng
        hand = Hand(cards = [Card(Rank.ACE, Suit.SPADE), Card(Rank.ACE, Suit.CLUB), Card(Rank.ACE, Suit.HEART)])
        self.assertTrue(hand.tong())
        self.assertEqual(hand.deng(), 5)

        # straight flush is 5 deng
        hand = Hand(cards = [Card(Rank.TWO, Suit.SPADE), Card(Rank.THREE, Suit.SPADE), Card(Rank.FOUR, Suit.SPADE)])
        self.assertTrue(hand.straight_flush())
        self.assertEqual(hand.deng(), 5)

        # straight is 3 deng
        hand = Hand(cards = [Card(Rank.TWO, Suit.SPADE), Card(Rank.THREE, Suit.CLUB), Card(Rank.FOUR, Suit.HEART)])
        self.assertTrue(hand.straight())
        self.assertEqual(hand.deng(), 3)

        # three yellow is 3 deng
        hand = Hand(cards = [Card(Rank.KING, Suit.SPADE), Card(Rank.QUEEN, Suit.CLUB), Card(Rank.QUEEN, Suit.HEART)])
        self.assertTrue(hand.three_yellow())
        self.assertEqual(hand.deng(), 3)

        # 3 cards same suit is 3 deng
        hand = Hand(cards = [Card(Rank.TWO, Suit.SPADE), Card(Rank.FIVE, Suit.SPADE), Card(Rank.QUEEN, Suit.SPADE)])
        self.assertEqual(hand.deng(), 3)

        # 3 cards different suit is 1 deng
        hand = Hand(cards = [Card(Rank.TWO, Suit.SPADE), Card(Rank.FIVE, Suit.SPADE), Card(Rank.QUEEN, Suit.HEART)])
        self.assertEqual(hand.deng(), 1)

if __name__ == '__main__':
    main()
