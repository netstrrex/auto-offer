# auto-offer
<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/HeadHunter_logo.png/600px-HeadHunter_logo.png" width="500">
</div>

### Описание

Простая в настройке и запуске утилита для тех, кто также, как и я устал страдать от того мракобесия, что сейчас творится на hh. Автоотказы, конченные фильтры, ИИ-рекрутеры и тому подобный шлак.
Изначально я хотел использовать вот этот замечательный [репозиторий](https://github.com/s3rgeym/hh-applicant-tool), но код там, мне показался сильно перегруженным, а настройка сложной. У автора этого репозитория также есть мобильное [приложение](https://github.com/s3rgeym/hh-resume-automate/releases), но к сожалению, там нет функционала генерации сопроводительного письма через ИИ.
Поэтому я решил ~~изобрести велосипед~~ написать свое решение этой проблемы.

P.s. большое спасибо тому человеку, что вытащил эндпоинты hh из их android приложения❤️

### Установка

```bash
$ git clone https://github.com/netstrrex/auto-offer.git
$ cd auto-offer
$ docker build . -t auto-offer:latest
```

### Настройка

Создайте .env файл в корне проекта и заполните его следующими значениями:

| Ключ | Значение |
| --- | --- |
| `HH__ACCESS_TOKEN` | Ваш access_token, получить его можно в этом мобильном [приложении](https://github.com/s3rgeym/hh-resume-automate/releases), после авторизации в вашем аккаунте на hh, в разделе "дополнительные настройки".|
| `HH__REFRESH_TOKEN` | Ваш refresh_token, получить его можно в этом мобильном [приложении](https://github.com/s3rgeym/hh-resume-automate/releases), после авторизации в вашем аккаунте на hh, в разделе "дополнительные настройки".|
| `HH__EXPIRED_AT` | Дата когда истекает токен,  получить его можно в этом мобильном [приложении](https://github.com/s3rgeym/hh-resume-automate/releases), после авторизации в вашем аккаунте на hh, в разделе "дополнительные настройки".|
| `HH__RESUME_ID` | ID вашего резюме, получить его можно [тут](https://hh.ru/applicant/resumes?hhtmFrom=main&hhtmFromLabel=header) из адресной строки, кликнув по нужному вам резюме.|
| `JOB__SEARCH_QUERY` | Строка для поиска нужных вам вакансий. У hh есть язык поисковых запросов, советую [почитать](https://hh.ru/article/1175).|
| `JOB__EXPERIENCE` | Ваш опыт работы в формате between1And3.|

### Запуск

```bash
$ docker run --env-file .env auto-offer
```
