import datetime
import uuid

from models.base import BasePModel


class FilmTimeStamp(BasePModel):
    jwt: str
    film_id: uuid.UUID
    film_timestamp: datetime.datetime
    event_time: datetime.datetime


class KafkaFilmTimeStamp(BasePModel):
    user_id: uuid.UUID
    film_id: uuid.UUID
    film_timestamp: datetime.datetime
    event_time: datetime.datetime
