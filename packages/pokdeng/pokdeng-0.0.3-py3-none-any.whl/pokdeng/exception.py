class BizException(Exception):
    pass

class DuplicateCards(BizException):
    def __init__(self):
        self.message = "Hand cannot have duplicate cards!"
        super().__init__(self.message)

class HandLessThan2Cards(BizException):
    def __init__(self):
        self.message = "Hand cannot have less than 2 cards!"
        super().__init__(self.message)

class HandMoreThan3Cards(BizException):
    def __init__(self):
        self.message = "Hand cannot have more than 3 cards!"
        super().__init__(self.message)

class GameLessThan1Player(BizException):
    def __init__(self):
        self.message = "Game cannot have less than 1 player!"
        super().__init__(self.message)

class GameMoreThan16Players(BizException):
    def __init__(self):
        self.message = "Game cannot have more than 16 players!"
        super().__init__(self.message)

class GameNoDealer(BizException):
    def __init__(self):
        self.message = "Game cannot have no dealer!"
        super().__init__(self.message)

class GamePocketMismatch(BizException):
    def __init__(self):
        self.message = "Game cannot have pocket mismatch!"
        super().__init__(self.message)
