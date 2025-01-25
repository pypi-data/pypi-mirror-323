from datetime import datetime


class Discount:
    def __init__(
            self,
            title: str,
            code: str,
            description: str,
            size: float,
            valid_until: datetime,
    ):
        self.title = title
        self.code = code
        self.description = description
        self.size = size
        self.valid_until = valid_until
