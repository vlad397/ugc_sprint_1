import abc
import uuid
from abc import ABC
from typing import Optional

from models.body import FilmTimeStamp, KafkaFilmTimeStamp
from svc.event_producer import EventProducer, KafkaEventProducer
from svc.user_parser import JWTUserParser, UserParser


class EventSendler(ABC):
    user_parser: UserParser
    event_producer: EventProducer

    @abc.abstractmethod
    def get_user(self, *args, **kwargs) -> uuid.UUID:
        pass

    @abc.abstractmethod
    def post_event(self, event_obj, topic):
        pass


class KafkaEventSendler(EventSendler):
    user_parser: JWTUserParser = JWTUserParser()
    event_producer: KafkaEventProducer

    def __init__(self, event_producer):
        self.event_producer = event_producer

    def post_event(self, event_obj: FilmTimeStamp, topic: str):
        user_id = self.get_user(event_obj.jwt)
        return self.event_producer.send(
            topic=topic, value=KafkaFilmTimeStamp(user_id=user_id, **event_obj.dict()).json().encode()
        )

    def get_user(self, jwt_token: str) -> uuid.UUID:
        return self.user_parser.get_user(jwt_token)


kafka_event_sendler: Optional[KafkaEventSendler] = None


def get_kafka_event_sendler() -> KafkaEventSendler:
    return kafka_event_sendler
