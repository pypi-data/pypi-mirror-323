import datetime
from typing import Optional, Any
from uuid import UUID

from subgate.domain.cycle import Cycle, CycleCode
from subgate.domain.discount import Discount
from subgate.domain.usage import UsageRate

ID = UUID


class Plan:
    def __init__(
            self,
            id: ID,
            title: str,
            price: float,
            currency: str,
            billing_cycle: Cycle,
            description: str,
            level: int,
            features: Optional[str],
            fields: dict[str, Any],
            usage_rates: list[UsageRate],
            discounts: list[Discount],
            created_at: datetime.datetime,
            updated_at: datetime.datetime,
    ):
        self.id = id
        self.title = title
        self.price = price
        self.currency = currency
        self.billing_cycle = billing_cycle
        self.description = description
        self.level = level
        self.features = features
        self.fields = fields
        self.usage_rates = usage_rates
        self.discounts = discounts
        self.created_at = created_at
        self.updated_at = updated_at


class PlanCreate:
    def __init__(
            self,
            title: str,
            price: float,
            currency: str,
            cycle: CycleCode | str = "Monthly",
            description: str = "",
            level: int = 10,
            features: str = "",
            usage_rates: list[UsageRate] = None,
            discounts: list[Discount] = None,
            fields: dict[str, Any] = None,
    ):
        self.title = title
        self.price = price
        self.currency = currency
        self.billing_cycle = Cycle.from_code(cycle)
        self.description = description
        self.level = level
        self.features = features
        self.usage_rates = usage_rates if usage_rates is not None else []
        self.discounts = discounts if discounts is not None else []
        self.fields = fields if fields is not None else {}
