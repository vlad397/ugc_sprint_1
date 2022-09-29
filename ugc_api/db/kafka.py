from typing import Optional

from aiokafka import AIOKafkaProducer
from kafka.admin import KafkaAdminClient

kafka_producer: Optional[AIOKafkaProducer] = None
kafka_admin: Optional[KafkaAdminClient] = None


async def get_kafka_producer() -> AIOKafkaProducer:
    return kafka_producer


def get_kafka_admin() -> KafkaAdminClient:
    return kafka_admin
