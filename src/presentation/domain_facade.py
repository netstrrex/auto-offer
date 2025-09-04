import asyncio
from asyncio import Semaphore
from collections.abc import Callable
from datetime import datetime
from logging import getLogger
from typing import Any

from domain.gpt.service import GptService
from domain.hh.service import HhService

logger = getLogger(__name__)


def exception_handler(func: Callable) -> Callable:
    async def wrapper(*args: tuple, **kwargs: dict) -> Any:
        try:
            res = await func(*args, **kwargs)
            return res
        except Exception as e:
            logger.exception(e)

    return wrapper


class DomainFacade:
    def __init__(self, hh_service: HhService, gpt_service: GptService) -> None:
        self._hh_service = hh_service
        self._gpt_service = gpt_service
        self._apply_counter = 0
        self._viewed_vacancies: set[str] = set()

    async def _process_vacancy(
        self, sem: Semaphore, user_first_name: str, vacancy_id: str
    ) -> None:
        async with sem:
            vacancy_detail = await self._hh_service.get_vacancy_detail(vacancy_id)
            user_prompt = (
                f"Имя: {user_first_name}\nВакансия: {vacancy_detail.description}"
            )
            cover_letter = await self._gpt_service.achat(user_prompt)
            await self._hh_service.apply_to_vacancy(vacancy_id, cover_letter)
        logger.info("Успешно отправлен отклик на вакансию %s", vacancy_detail.name)
        self._apply_counter += 1

    async def lift_resume_forever(self) -> None:
        while True:

            @exception_handler
            async def process_resume_lift() -> None:
                resume_detail = await self._hh_service.get_resume_detail()
                if resume_detail["can_publish_or_update"]:
                    await self._hh_service.lift_resume()
                    logger.info("Резюме успешно поднято в поиске")
                else:
                    next_publish_time = datetime.strptime(
                        resume_detail["next_publish_at"], "%Y-%m-%dT%H:%M:%S%z"
                    )
                    timezone = next_publish_time.tzinfo
                    now_in_timezone = datetime.now(timezone)
                    sleep_seconds = int(
                        (next_publish_time - now_in_timezone).total_seconds()
                    )
                    hours = sleep_seconds // 3600
                    minutes = (sleep_seconds % 3600) // 60
                    logger.info(
                        "Поднять резюме в поиске пока нельзя, засыпаем на %dч %dм...",
                        hours,
                        minutes,
                    )
                    await asyncio.sleep(sleep_seconds + 5)

            await process_resume_lift()

    async def apply_to_vacancies_forever(self) -> None:
        resume_detail = await self._hh_service.get_resume_detail()
        user_first_name = resume_detail["first_name"]
        sem = Semaphore(5)
        while True:

            @exception_handler
            async def process_apply_to_vacancies() -> None:
                vacancies_ids = await self._hh_service.get_vacancies_ids()
                new_vacancies = self._viewed_vacancies ^ vacancies_ids
                self._viewed_vacancies.update(new_vacancies)
                if self._apply_counter >= 150:
                    logger.info(
                        "Достигнут суточный лимит откликов. Засыпаем на стуки..."
                    )
                    await asyncio.sleep(60 * 60 * 24)
                    self._apply_counter = 0
                tasks = tuple(
                    self._process_vacancy(sem, user_first_name, vacancy_id)
                    for vacancy_id in new_vacancies
                )
                await asyncio.gather(*tasks)
                logger.info("Подходящие вакансии закончились. Засыпаем на час...")
                await asyncio.sleep(60 * 60)

            await process_apply_to_vacancies()
