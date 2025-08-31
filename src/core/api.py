import datetime
from abc import ABC, abstractmethod
from typing import Any


class AbstractHhApi(ABC):
    api_url = "https://api.hh.ru"
    auth_url = "https://hh.ru/oauth/token"

    def __init__(
        self, access_token: str, refresh_token: str, expired_at: datetime.datetime
    ) -> None:
        self._refresh_token = refresh_token
        self._expired_at = expired_at
        self._headers = {
            "User-Agent": "YourAppName/1.0",
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

    async def _ensure_token(self) -> None:
        if datetime.datetime.now() >= self._expired_at:
            await self._refresh_access_token()

    @abstractmethod
    async def _refresh_access_token(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        raise NotImplementedError()

    @abstractmethod
    async def post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        raise NotImplementedError
