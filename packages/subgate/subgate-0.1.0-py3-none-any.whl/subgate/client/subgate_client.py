from subgate.client.base_client import AsyncBaseClient, SyncBaseClient
from subgate.client.plan_client import AsyncPlanClient, SyncPlanClient
from subgate.client.subscription_client import AsyncSubscriptionClient, SyncSubscriptionClient
from subgate.client.webhook_client import AsyncWebhookClient, SyncWebhookClient


class AsyncSubgateClient:
    def __init__(self, base_url: str, apikey: str):
        client = AsyncBaseClient(base_url, apikey)
        self.plan_client = AsyncPlanClient(client)
        self.subscription_client = AsyncSubscriptionClient(client)
        self.webhook_client = AsyncWebhookClient(client)


class SubgateClient:
    def __init__(self, base_url: str, apikey: str):
        client = SyncBaseClient(base_url, apikey)
        self.plan_client = SyncPlanClient(client)
        self.subscription_client = SyncSubscriptionClient(client)
        self.webhook_client = SyncWebhookClient(client)
