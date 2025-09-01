import asyncio
import re
from asyncio import Semaphore
from dataclasses import dataclass
from typing import Any, cast

from core.api import AbstractHhApi


@dataclass
class VacancyDetail:
    name: str
    description: str


class HhService:
    def __init__(
        self,
        hh_api: AbstractHhApi,
        resume_id: str,
        experience: str,
        vacancy_search_query: str,
    ) -> None:
        self._hh_api = hh_api
        self._resume_id = resume_id
        self._experience = experience
        self._vacancy_search_query = vacancy_search_query

    async def _get_page_vacancies_ids(
        self, sem: Semaphore, params: dict[str, Any], experience: str
    ) -> set[str]:
        async with sem:
            vacancies = cast(
                dict[str, Any], await self._hh_api.get("/vacancies", params=params)
            )
        return {
            vacancy["id"]
            for vacancy in vacancies["items"]
            if vacancy["experience"]["id"] == experience
        }

    async def get_resume_detail(self) -> dict[str, Any]:
        resume_detail = cast(
            dict[str, Any], await self._hh_api.get(f"/resumes/{self._resume_id}")
        )
        return resume_detail

    async def get_vacancy_detail(self, vacancy_id: str) -> VacancyDetail:
        result = cast(
            dict[str, Any], await self._hh_api.get(f"/vacancies/{vacancy_id}")
        )
        clear_details = re.sub(r"(\<(/?[^>]+)>)", "", result["description"])
        return VacancyDetail(result["name"], clear_details)

    async def lift_resume(self) -> None:
        await self._hh_api.post(f"/resumes/{self._resume_id}/publish")

    async def get_vacancies_ids(self) -> set[str]:
        sem = Semaphore(5)
        params = {"page": 0, "text": self._vacancy_search_query}
        first_result = cast(
            dict[str, Any], await self._hh_api.get("/vacancies", params)
        )
        pages = first_result["pages"]
        tasks = tuple(
            self._get_page_vacancies_ids(
                sem,
                {"page": page, "text": self._vacancy_search_query},
                self._experience,
            )
            for page in range(pages)
        )
        result = await asyncio.gather(*tasks)
        ids = set().union(*result)
        return ids

    async def apply_to_vacancy(self, vacancy_id: str, cover_letter: str) -> None:
        params = {
            "resume_id": self._resume_id,
            "vacancy_id": vacancy_id,
            "message": cover_letter,
        }
        await self._hh_api.post("/negotiations", params=params)
