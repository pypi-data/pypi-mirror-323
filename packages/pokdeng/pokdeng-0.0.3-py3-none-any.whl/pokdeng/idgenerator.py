from uuid import uuid4

class CardHolderId:
    def __init__(self):
        self.value: str = str(uuid4())
