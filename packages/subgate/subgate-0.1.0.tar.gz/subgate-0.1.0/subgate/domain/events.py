from enum import StrEnum


class EventCode(StrEnum):
    PlanCreated = "PlanCreated"
    PlanUpdated = "PlanUpdated"
    PlanDeleted = "PlanDeleted"
    SubscriptionCreated = "SubscriptionCreated"
    SubscriptionUpdated = "SubscriptionUpdated"
    SubscriptionDeleted = "SubscriptionDeleted"
    SubscriptionExpired = "SubscriptionExpired"
    SubscriptionPaused = "SubscriptionPaused"
    SubscriptionResumed = "SubscriptionResumed"
    SubscriptionRenewed = "SubscriptionRenewed"
    LastBillingChanged = "LastBillingChanged"
    ActiveSubscriptionChanged = "ActiveSubscriptionChanged"
