from enum import StrEnum


class CycleCode(StrEnum):
    Daily = "Daily"
    Weekly = "Weekly"
    Monthly = "Monthly"
    Quarterly = "Quarterly"
    Semiannual = "Semiannual"
    Annual = "Annual"


class Cycle:
    def __init__(
            self,
            title: str,
            code: CycleCode,
            cycle_in_days: int,
    ):
        self.title = title
        self.code = code
        self.cycle_in_days = cycle_in_days

    @classmethod
    def from_code(cls, code: CycleCode):
        if code == "Daily":
            return cls("Daily", code, 1)
        if code == "Weekly":
            return cls("Weekly", code, 7)
        if code == "Monthly":
            return cls("Monthly", code, 31)
        if code == "Quarterly":
            return cls("Quarterly", code, 92)
        if code == "Semiannual":
            return cls("Semiannual", code, 183)
        if code == "Annual":
            return cls("Annual", code, 365)
        raise ValueError(code)
