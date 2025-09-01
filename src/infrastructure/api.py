import datetime
from collections.abc import AsyncGenerator
from logging import getLogger
from typing import Any

from aiohttp import ClientSession

from core.api import AbstractHhApi

logger = getLogger(__name__)


async def session_generator() -> AsyncGenerator[ClientSession, Any]:
    async with ClientSession() as session:
        while True:
            yield session


class HhApi(AbstractHhApi):
    def __init__(
        self, access_token: str, refresh_token: str, expired_at: datetime.datetime
    ) -> None:
        super().__init__(access_token, refresh_token, expired_at)
        self._session_generator = session_generator()

    async def _refresh_access_token(self) -> None:
        data = {"grant_type": "refresh_token", "refresh_token": self._refresh_token}
        headers = {
            "User-Agent": "YourAppName/1.0",
            "Accept": "application/json",
        }
        session = await anext(self._session_generator)
        async with session.post(self.auth_url, data=data, headers=headers) as response:
            response_json = await response.json()
            self._access_token = response_json["access_token"]
            self._refresh_token = response_json.get(
                "refresh_token", self._refresh_token
            )
            self._expired_at += datetime.timedelta(weeks=2)

    async def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        session = await anext(self._session_generator)
        await self._ensure_token()
        async with session.get(
            url=self.api_url + url, params=params, headers=self._headers
        ) as response:
            if response.status == 204:
                return None
            response_json = await response.json()
        return response_json

    async def post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        session = await anext(self._session_generator)
        await self._ensure_token()
        async with session.post(
            self.api_url + url, data=data, params=params, headers=self._headers
        ) as response:
            if response.status in (201, 204):
                return None
            response_json = await response.json()
        return response_json
