# Проектная работа 8 спринта

Проектные работы в этом модуле выполняются в командах по 3 человека. Процесс обучения аналогичен сервису, где вы изучали асинхронное программирование. Роли в команде и отправка работы на ревью не меняются.

Распределение по командам подготовит команда сопровождения. Куратор поделится с вами списками в Slack в канале #group_projects.

Задания на спринт вы найдёте внутри тем.
### Ссылка
  https://github.com/Chelovek760/ugc_sprint_1_g
### Запуск
- C dev окружением:  
docker-compose -f docker-compose-dev.yml up
- С prod окружением:  
docker-compose up    
- Сервис будет доступен по http://localhost:8000
- Документация 
http://localhost:8000/api/docs
  <br/>
  <br/>
### Задачи
См. [issue](https://github.com/Chelovek760/ugc_sprint_1_g/issues?q=is%3Aissue+is%3Aclosed)
### Результаты анализа
См. [benchmark](https://github.com/vlad397/ugc_sprint_1/tree/main/benchmark)
###  Принципиальная схема работы приложения
1. Post запросом на /api/film-timestamp/ в body передаются:
- jwt: str
- film_id: uuid.UUID
- film_timestamp: datetime.datetime
- event_time: datetime.datetime 

2. Данные предобрабатываются и отпраляются в kafka
3. С помощью [Kafka Engine ](https://clickhouse.com/docs/ru/engines/table-engines/integrations/kafka/) реализуется ETL Kafka->ClickHouse
4. \*profit\*

