from datetime import datetime
from enum import StrEnum
from typing import Optional

from subgate.domain.plan import ID, Plan
from subgate.domain.usage import Usage


class SubscriptionStatus(StrEnum):
    Active = "Active"
    Paused = "Paused"
    Expired = "Expired"


class Subscription:
    def __init__(
            self,
            id: ID,
            subscriber_id: str,
            plan: Plan,
            status: SubscriptionStatus,
            created_at: datetime,
            updated_at: datetime,
            last_billing: datetime,
            paused_from: Optional[datetime],
            autorenew: bool,
            usages: list[Usage],
    ):
        self.id = id
        self.subscriber_id = subscriber_id
        self.plan = plan
        self.status = status
        self.paused_from = paused_from
        self.created_at = created_at
        self.updated_at = updated_at
        self.last_billing = last_billing
        self.autorenew = autorenew
        self.usages = usages

    @property
    def days_left(self) -> int:
        raise NotImplemented


class SubscriptionCreate:
    def __init__(
            self,
            plan: Plan,
            subscriber_id: str,
            status: SubscriptionStatus = "Active",
            usages: list[Usage] = None,
            paused_from: Optional[datetime] = None,
            autorenew: bool = False,
    ):
        self.plan = plan
        self.subscriber_id = subscriber_id
        self.status = status
        self.usages = usages if usages else [Usage.from_usage_rate(x) for x in plan.usage_rates]
        self.paused_from = paused_from
        self.autorenew = autorenew
