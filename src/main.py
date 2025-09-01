import asyncio
import logging

from colorlog import ColoredFormatter

from config import settings
from domain.gpt.service import GptService
from domain.hh.service import HhService
from infrastructure.api import HhApi
from presentation.domain_facade import DomainFacade
from prompt import COVER_LETTER_PROMPT

logging.getLogger("asyncio").setLevel(logging.CRITICAL)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = ColoredFormatter(
    fmt="%(log_color)s%(asctime)s | %(name)-35s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    },
)
console_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)


async def main() -> None:
    hh_api = HhApi(
        settings.hh.access_token,
        settings.hh.refresh_token,
        settings.hh.expired_at,
    )

    hh_service = HhService(
        hh_api,
        settings.hh.resume_id,
        settings.job.experience,
        settings.job.search_query,
    )

    gpt_service = GptService(COVER_LETTER_PROMPT, "gpt-4o", temperature=0.5, top_p=0.8)

    facade = DomainFacade(hh_service, gpt_service)
    await asyncio.gather(
        facade.lift_resume_forever(), facade.apply_to_vacancies_forever()
    )


if __name__ == "__main__":
    asyncio.run(main())
