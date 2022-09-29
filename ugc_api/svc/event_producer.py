import abc
from abc import ABC
from typing import Optional, Set

import backoff
import requests
from aiokafka import AIOKafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic


class EventProducer(ABC):
    def __init__(self, event_producer):
        self.event_producer = event_producer

    @abc.abstractmethod
    def send(self, topic: str, value: str, *args, **kwargs):
        pass


class KafkaEventProducer(EventProducer):
    event_producer: AIOKafkaProducer
    admin_client: KafkaAdminClient

    def __init__(self, event_producer, kafka_admin, topics: Set[str]):
        super().__init__(event_producer)
        self.admin_client = kafka_admin
        topics_list = []
        existing_topics = set(self.admin_client.list_topics())
        added_topics = topics - existing_topics
        for topic in added_topics:
            topics_list.append(NewTopic(name=topic, num_partitions=1, replication_factor=1))
        self.admin_client.create_topics(new_topics=topics_list, validate_only=False)
        self.topics = existing_topics.union(topics)

    @backoff.on_exception(backoff.expo, requests.exceptions.Timeout)
    def send(self, topic: str, value: bytes, *args, **kwargs):
        return self.event_producer.send(topic=topic, value=value, *args, **kwargs)


kafka_event_producer: Optional[KafkaEventProducer] = None


def get_kafka_event_producer() -> KafkaEventProducer:
    return kafka_event_producer
