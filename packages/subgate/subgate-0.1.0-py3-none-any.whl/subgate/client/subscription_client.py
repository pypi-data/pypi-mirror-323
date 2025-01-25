import datetime
from typing import Optional, Iterable

from subgate.client.base_client import OrderBy, _build_query_params, AsyncBaseClient, SyncBaseClient
from subgate.domain.plan import ID, Plan
from subgate.domain.subscription import Subscription, SubscriptionStatus, SubscriptionCreate
from subgate.domain.usage import Usage, UsageForm
from subgate.services import serializers, deserializers
from subgate.services.validators import validate


class AsyncSubscriptionClient:
    def __init__(self, client: AsyncBaseClient):
        self._client = client

    async def get_subscription_by_id(self, sub_id: ID) -> Subscription:
        response_data = await self._client.request("GET", f"/subscription/{sub_id}")
        result = deserializers.deserialize_subscription(response_data)
        validate(result)
        return result

    async def get_active_subscription(self, subscriber_id: str) -> Optional[Subscription]:
        response_data = await self._client.request("GET", f"/subscription/active-one/{subscriber_id}")
        if response_data:
            result = deserializers.deserialize_subscription(response_data)
            validate(result)
            return result
        return None

    async def get_selected_subscriptions(
            self,
            ids: Iterable[ID] = None,
            subscriber_ids: Iterable[str] = None,
            statuses: Iterable[SubscriptionStatus] = None,
            expiration_date_gte: datetime.datetime = None,
            expiration_date_lt: datetime.datetime = None,
            skip: int = 0,
            limit: int = 100,
            order_by: OrderBy = None,
            asc: bool = None,
    ) -> list[Subscription]:
        params = _build_query_params(
            ids=ids,
            subscriber_ids=subscriber_ids,
            statuses=statuses,
            expiration_date_gte=expiration_date_gte,
            expiration_date_lt=expiration_date_lt,
            skip=skip,
            limit=limit,
            order_by=order_by,
            asc=asc,
        )
        response_data = await self._client.request("GET", f"/subscription", params=params)
        result = []
        for json in response_data:
            sub = deserializers.deserialize_subscription(json)
            validate(sub)
            result.append(sub)
        return result

    async def create_subscription(
            self,
            subscriber_id: str,
            plan: Plan,
            usages: list[Usage] = None,
            autorenew: bool = False,
    ) -> Subscription:
        sub_create = SubscriptionCreate(
            plan=plan,
            subscriber_id=subscriber_id,
            status="Active",
            paused_from=None,
            autorenew=autorenew,
            usages=usages,
        )
        validate(sub_create)
        payload = serializers.serialize_subscription_create(sub_create)
        response = await self._client.request("POST", "/subscription", json=payload)
        created = deserializers.deserialize_subscription(response)
        validate(created)
        return created

    async def update_subscription(self, subscription: Subscription) -> None:
        validate(subscription)
        payload = serializers.serialize_subscription(subscription)
        await self._client.request("PUT", f"/subscription/{subscription.id}", json=payload)

    async def update_subscription_plan(self, sub_id: ID, plan: Plan) -> None:
        validate(plan)
        payload = serializers.serialize_plan(plan)
        await self._client.request("PATCH", f"/subscription/{sub_id}/update-plan", json=payload)

    async def delete_subscription_by_id(self, sub_id: ID) -> None:
        await self._client.request("DELETE", f"/subscription/{sub_id}")

    async def delete_selected_subscriptions(
            self,
            ids: Iterable[ID] = None,
            subscriber_ids: Iterable[str] = None,
            statuses: Iterable[SubscriptionStatus] = None,
            expiration_date_gte: datetime.datetime = None,
            expiration_date_lt: datetime.datetime = None,
    ) -> None:
        sby = _build_query_params(
            ids=ids,
            subscriber_ids=subscriber_ids,
            statuses=statuses,
            expiration_date_gte=expiration_date_gte,
            expiration_date_lt=expiration_date_lt,
        )
        await self._client.request("DELETE", f"/subscription", json=sby)

    async def pause_subscription(self, sub_id: ID) -> None:
        await self._client.request("PATCH", f"/subscription/{sub_id}/pause")

    async def resume_subscription(self, sub_id: ID) -> None:
        await self._client.request("PATCH", f"/subscription/{sub_id}/resume")

    async def renew_subscription(self, sub_id: ID, from_date: datetime.datetime = None) -> None:
        payload = from_date.isoformat() if from_date else None
        await self._client.request("PATCH", f"/subscription/{sub_id}/renew", json=payload)

    async def add_usages(self, sub_id: ID, usages: list[Usage]) -> None:
        validate(usages)
        payload = [serializers.serialize_usage(usage) for usage in usages]
        await self._client.request("PATCH", f"/subscription/{sub_id}/add-usages", json=payload)

    async def remove_usages(self, sub_id: ID, resources: list[str]) -> None:
        await self._client.request("PATCH", f"/subscription/{sub_id}/remove-usages", json=resources)

    async def update_usages(self, sub_id: ID, usages: list[Usage]) -> None:
        validate(usages)
        payload = [serializers.serialize_usage(usage) for usage in usages]
        await self._client.request("PATCH", f"/subscription/{sub_id}/update-usages", json=payload)

    async def increase_usage(self, sub_id: ID, resource: str, value: float) -> None:
        """
        This is not an idempotent operation; it increases usage by the given value.
        If the value is less than zero, it decreases the usage instead.
        If no usage record is found for the specified resource, an `ItemNotExist` error is raised.
        """
        payload = serializers.serialize_usage_form(UsageForm(resource, value))
        await self._client.request("PATCH", f"/subscription/{sub_id}/increase-usage", params=payload)


class SyncSubscriptionClient:
    def __init__(self, client: SyncBaseClient):
        self._client = client

    def get_subscription_by_id(self, sub_id: ID) -> Subscription:
        response_data = self._client.request("GET", f"/subscription/{sub_id}")
        result = deserializers.deserialize_subscription(response_data)
        validate(result)
        return result

    def get_active_subscription(self, subscriber_id: str) -> Optional[Subscription]:
        response_data = self._client.request("GET", f"/subscription/active-one/{subscriber_id}")
        if response_data:
            result = deserializers.deserialize_subscription(response_data)
            validate(result)
            return result
        return None

    def get_selected_subscriptions(
            self,
            ids: Iterable[ID] = None,
            subscriber_ids: Iterable[str] = None,
            statuses: Iterable[SubscriptionStatus] = None,
            expiration_date_gte: datetime.datetime = None,
            expiration_date_lt: datetime.datetime = None,
            skip: int = 0,
            limit: int = 100,
            order_by: OrderBy = None,
            asc: bool = None,
    ) -> list[Subscription]:
        params = _build_query_params(
            ids=ids,
            subscriber_ids=subscriber_ids,
            statuses=statuses,
            expiration_date_gte=expiration_date_gte,
            expiration_date_lt=expiration_date_lt,
            skip=skip,
            limit=limit,
            order_by=order_by,
            asc=asc,
        )
        response_data = self._client.request("GET", f"/subscription", params=params)
        result = []
        for json in response_data:
            sub = deserializers.deserialize_subscription(json)
            validate(sub)
            result.append(sub)
        return result

    def create_subscription(
            self,
            subscriber_id: str,
            plan: Plan,
            usages: list[Usage] = None,
            autorenew: bool = False,
    ) -> Subscription:
        sub_create = SubscriptionCreate(
            plan=plan,
            subscriber_id=subscriber_id,
            status="Active",
            paused_from=None,
            autorenew=autorenew,
            usages=usages,
        )
        validate(sub_create)
        payload = serializers.serialize_subscription_create(sub_create)
        response = self._client.request("POST", "/subscription", json=payload)
        created = deserializers.deserialize_subscription(response)
        validate(created)
        return created

    def update_subscription(self, subscription: Subscription) -> None:
        validate(subscription)
        payload = serializers.serialize_subscription(subscription)
        self._client.request("PUT", f"/subscription/{subscription.id}", json=payload)

    def update_subscription_plan(self, sub_id: ID, plan: Plan) -> None:
        validate(plan)
        payload = serializers.serialize_plan(plan)
        self._client.request("PATCH", f"/subscription/{sub_id}/update-plan", json=payload)

    def delete_subscription_by_id(self, sub_id: ID) -> None:
        self._client.request("DELETE", f"/subscription/{sub_id}")

    def delete_selected_subscriptions(
            self,
            ids: Iterable[ID] = None,
            subscriber_ids: Iterable[str] = None,
            statuses: Iterable[SubscriptionStatus] = None,
            expiration_date_gte: datetime.datetime = None,
            expiration_date_lt: datetime.datetime = None,
    ) -> None:
        sby = _build_query_params(
            ids=ids,
            subscriber_ids=subscriber_ids,
            statuses=statuses,
            expiration_date_gte=expiration_date_gte,
            expiration_date_lt=expiration_date_lt,
        )
        self._client.request("DELETE", f"/subscription", json=sby)

    def pause_subscription(self, sub_id: ID) -> None:
        self._client.request("PATCH", f"/subscription/{sub_id}/pause")

    def resume_subscription(self, sub_id: ID) -> None:
        self._client.request("PATCH", f"/subscription/{sub_id}/resume")

    def renew_subscription(self, sub_id: ID, from_date: datetime.datetime = None) -> None:
        payload = from_date.isoformat() if from_date else None
        self._client.request("PATCH", f"/subscription/{sub_id}/renew", json=payload)

    def add_usages(self, sub_id: ID, usages: list[Usage]) -> None:
        validate(usages)
        payload = [serializers.serialize_usage(usage) for usage in usages]
        self._client.request("PATCH", f"/subscription/{sub_id}/add-usages", json=payload)

    def remove_usages(self, sub_id: ID, resources: list[str]) -> None:
        self._client.request("PATCH", f"/subscription/{sub_id}/remove-usages", json=resources)

    def update_usages(self, sub_id: ID, usages: list[Usage]) -> None:
        validate(usages)
        payload = [serializers.serialize_usage(usage) for usage in usages]
        self._client.request("PATCH", f"/subscription/{sub_id}/update-usages", json=payload)

    def increase_usage(self, sub_id: ID, resource: str, value: float) -> None:
        """
        This is not an idempotent operation; it increases usage by the given value.
        If the value is less than zero, it decreases the usage instead.
        If no usage record is found for the specified resource, an `ItemNotExist` error is raised.
        """
        payload = serializers.serialize_usage_form(UsageForm(resource, value))
        self._client.request("PATCH", f"/subscription/{sub_id}/increase-usage", params=payload)
