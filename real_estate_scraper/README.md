# Микросервис Scraper

В данном микросервисе реализованы скрипты для сбора данных с вебсайтов по продаже недвижимости.

## Запуск паука (парсера)

Для запуска паука можно использовать команду:
```
cd real_estate_scraper
scrapy crawl cityexpert_belgrade
```
Для запуска паука и сохранения полученных данный в json файл можно использовать команду:
```
scrapy crawl cityexpert_belgrade -o file_name.json
```

## Разработчики
[![GitHub](https://img.shields.io/badge/-Бучельников_Александр-black?style=for-the-badge&logo=GitHub)](https://github.com/AVanslov)
[![GitHub](https://img.shields.io/badge/-Саликов_Никита-black?style=for-the-badge&logo=GitHub)](https://github.com/Nikita528)