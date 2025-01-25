import datetime
import logging
from typing import Optional, Iterable

import httpx

from subgate.client.exceptions import ValidationError, ItemNotExist, ItemAlreadyExist, MultipleError
from subgate.domain.plan import ID
from subgate.domain.subscription import (
    SubscriptionStatus,
)

OrderBy = list[str]

logger = logging.getLogger(__name__)


def _build_query_params(
        ids: Optional[Iterable[ID]] = None,
        subscriber_ids: Optional[Iterable[str]] = None,
        statuses: Optional[Iterable[SubscriptionStatus]] = None,
        expiration_date_gte: Optional[datetime.datetime] = None,
        expiration_date_lt: Optional[datetime.datetime] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[OrderBy] = None,
        asc: Optional[bool] = None,
) -> dict:
    params = {}
    if ids is not None:
        if not isinstance(ids, Iterable):
            ids = [ids]
        params["ids"] = [str(x) for x in ids]
    if subscriber_ids is not None:
        params["subscriber_ids"] = list(subscriber_ids)
    if statuses is not None:
        params["statuses"] = [statuses] if isinstance(statuses, str) else list(statuses)
    if expiration_date_gte:
        params["expiration_date_gte"] = expiration_date_gte.isoformat()
    if expiration_date_lt:
        params["expiration_date_lt"] = expiration_date_lt.isoformat()
    if skip is not None:
        params["skip"] = skip
    if limit is not None:
        params["limit"] = limit
    if order_by is not None:
        params["order_by"] = order_by
    if asc is not None:
        params["asc"] = 1 if asc else -1
    return params


def _processing_response(response: httpx.Response):
    if response.status_code == 404:
        data = response.json().get("detail")
        if not data:
            response.raise_for_status()
        raise ItemNotExist.from_json(data)

    if response.status_code == 409:
        data = response.json()["detail"]
        raise ItemAlreadyExist.from_json(data)

    if response.status_code >= 400:
        response.raise_for_status()

    if response.status_code == 204:
        return None
    return response.json()


class BaseClient:

    def __init__(self, base_url: str, apikey: str):
        self._base_url = base_url
        self._apikey = apikey
        self._headers = {
            "Apikey-Value": f"{apikey}",
            "Content-Type": "application/json",
        }


class AsyncBaseClient(BaseClient):
    def __init__(self, base_url: str, apikey: str):
        super().__init__(base_url, apikey)
        self._client = httpx.AsyncClient(headers=self._headers, follow_redirects=True)

    async def request(self, method: str, endpoint: str, **kwargs) -> Optional[dict]:
        url = f"{self._base_url}{endpoint}"
        headers = self._headers | kwargs.pop("headers", {})
        response = await self._client.request(method, url, headers=headers, **kwargs)
        return _processing_response(response)


class SyncBaseClient(BaseClient):
    def __init__(self, base_url: str, apikey: str):
        super().__init__(base_url, apikey)
        self._client = httpx.Client(headers=self._headers, follow_redirects=True)

    def request(self, method: str, endpoint: str, **kwargs) -> Optional[dict]:
        url = f"{self._base_url}{endpoint}"
        headers = {**self._headers, **kwargs.pop("headers", {})}
        response = self._client.request(method, url, headers=headers, **kwargs)
        return _processing_response(response)
