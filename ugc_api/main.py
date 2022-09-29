import socket

from aiokafka import AIOKafkaProducer
from api.v1 import ugc
from core import config
from db import kafka
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from svc import event_producer, event_sendler

from kafka import KafkaAdminClient

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/docs",
    openapi_url="/api/docs.json",
    default_response_class=ORJSONResponse,
    debug=config.DEBUG,
)


@app.on_event("startup")
async def startup():
    kafka.kafka_admin = KafkaAdminClient(
        bootstrap_servers=f"{config.KAFKA_HOST}:{config.KAFKA_PORT}", client_id=socket.gethostname()
    )
    kafka.kafka_producer = AIOKafkaProducer(
        bootstrap_servers=[f"{config.KAFKA_HOST}:{config.KAFKA_PORT}"], client_id=socket.gethostname()
    )
    await kafka.kafka_producer.start()
    event_producer.kafka_event_producer = event_producer.KafkaEventProducer(
        event_producer=kafka.kafka_producer,
        kafka_admin=kafka.kafka_admin,
        topics=set(
            "film_timestamp",
        ),
    )
    event_sendler.kafka_event_sendler = event_sendler.KafkaEventSendler(
        event_producer=event_producer.kafka_event_producer
    )


@app.on_event("shutdown")
async def shutdown():
    await kafka.kafka_producer.stop()
    kafka.kafka_admin.close()


app.include_router(ugc.router, prefix=f"/api/{config.API_VERSION}/films", tags=["ugc"])
