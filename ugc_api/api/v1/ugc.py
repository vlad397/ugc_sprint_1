from http import HTTPStatus

from fastapi import APIRouter, Depends
from models.body import FilmTimeStamp
from svc.event_sendler import KafkaEventSendler, get_kafka_event_sendler

router = APIRouter()


@router.post("/film-timestamp/")
async def film_timestamp(
    film_timestamp: FilmTimeStamp, kafka_event_sendler: KafkaEventSendler = Depends(get_kafka_event_sendler)
) -> HTTPStatus.OK:
    await kafka_event_sendler.post_event(topic="film_timestamp", event_obj=film_timestamp)
    return HTTPStatus.OK
