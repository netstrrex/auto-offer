from collections.abc import Callable
from logging import getLogger

import g4f
from g4f.Provider import __all__ as all_providers
from g4f.providers.types import BaseProvider
from g4f.typing import Message

logger = getLogger(__name__)


class GptService:
    def __init__(
        self,
        system_prompt: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        top_p: float = 0.95,
    ):
        self._system_prompt = system_prompt
        self._model = model
        self._temperature = temperature
        self._top_p = top_p
        self._providers = [getattr(g4f.Provider, p) for p in all_providers]

    def _make_messages(self, user_prompt: str) -> list[Message]:
        return [
            Message({"role": "system", "content": self._system_prompt}),
            Message({"role": "user", "content": user_prompt}),
        ]

    async def _try_providers(self, func: Callable) -> str:
        last_error = None
        for provider in self._providers:
            try:
                res = await func(provider)
                if res == "":
                    continue
                return res
            except Exception as e:
                last_error = e
                continue
        raise last_error or RuntimeError("No working provider found")

    async def achat(self, user_prompt: str) -> str:
        messages = self._make_messages(user_prompt)

        async def _call(provider: type[BaseProvider]) -> str:
            return await g4f.ChatCompletion.create_async(
                model=self._model,
                provider=provider,
                messages=messages,
                temperature=self._temperature,
                top_p=self._top_p,
            )

        return await self._try_providers(_call)
