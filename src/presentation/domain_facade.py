import asyncio
from asyncio import Semaphore
from datetime import datetime
from logging import getLogger

from domain.gpt.service import GptService
from domain.hh.service import HhService

logger = getLogger(__name__)


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
            resume_detail = await self._hh_service.get_resume_detail()
            if not resume_detail["can_publish_or_update"]:
                next_publish_time = datetime.strptime(
                    resume_detail["next_publish_at"], "%Y-%m-%dT%H:%M:%S%z"
                )
                timezone = next_publish_time.tzinfo
                now_in_timezone = datetime.now(timezone)
                sleep_seconds = (next_publish_time - now_in_timezone).seconds
                await asyncio.sleep(sleep_seconds)
            await self._hh_service.lift_resume()
            logger.info("Резюме успешно поднято в поиске")

    async def apply_to_vacancies_forever(self) -> None:
        resume_detail = await self._hh_service.get_resume_detail()
        user_first_name = resume_detail["first_name"]
        sem = Semaphore(5)
        while True:
            vacancies_ids = await self._hh_service.get_vacancies_ids()
            new_vacancies = self._viewed_vacancies ^ vacancies_ids
            self._viewed_vacancies.update(new_vacancies)
            if self._apply_counter >= 150:
                logger.info("Достигнут суточный лимит откликов. Засыпаем на стуки...")
                await asyncio.sleep(60 * 60 * 24)
                self._apply_counter = 0
            tasks = tuple(
                self._process_vacancy(sem, user_first_name, vacancy_id)
                for vacancy_id in new_vacancies
            )
            await asyncio.gather(*tasks)
            logger.info("Подходящие вакансии закончились. Засыпаем на час...")
            await asyncio.sleep(60 * 60)
