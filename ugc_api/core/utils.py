import datetime
import logging
import random
import uuid
from queue import Queue
from threading import Thread

import jwt
import requests
from models.body import FilmTimeStamp

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ThreadPost(Thread):
    def __init__(self, queue, save_func):
        Thread.__init__(self)
        self.queue = queue
        self.save_func = save_func

    def run(self):
        while True:
            ti = self.queue.get()
            try:
                self.save_func(ti)
            finally:
                self.queue.task_done()


class Spamer:
    user_ids: set = set()
    film_ids: set = set()

    def __init__(
        self,
        url: str,
        n_users: int = 10000,
        n_films: int = 10000,
        n_posts: int = 1000000,
        n_workers=10,
        jwt_secret: str = "qwerty",
    ):
        self.url = url
        self.n_users = n_users
        self.n_films = n_films
        self.n_posts = n_posts
        self.n_workers = n_workers
        self.jwt_secret = jwt_secret
        self._generate_film_id()
        self._generate_user_id()

    def _generate_element(self) -> FilmTimeStamp:
        return FilmTimeStamp(
            jwt=jwt.encode(
                dict(
                    user_id=str(random.sample(self.user_ids, 1)[0]),
                    exp=datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=5),
                    iat=datetime.datetime.now(tz=datetime.timezone.utc),
                ),
                self.jwt_secret,
            ),
            film_id=str(random.sample(self.film_ids, 1)[0]),
            film_timestamp=datetime.datetime.now(),
            event_time=datetime.datetime.now(),
        )

    def data_generator(self):
        posts_now = 0
        while self.n_posts > posts_now:
            yield self._generate_element()
            posts_now += 1

    def _generate_user_id(self):
        while len(self.user_ids) < self.n_users:
            self.user_ids.add(uuid.uuid4())

    def _generate_film_id(self):
        while len(self.film_ids) < self.n_films:
            self.film_ids.add(uuid.uuid4())

    def post(self, data: FilmTimeStamp):
        requests.post(url=self.url, data=data.json())

    def threading_post(self):
        queue = Queue()
        for _ in range(self.n_workers):
            worker = ThreadPost(queue, self.post)
            worker.daemon = True
            worker.start()
        return queue

    def spam(self, user_threads=False):
        if user_threads:
            queue = self.threading_post()
        for data in self.data_generator():
            if user_threads:
                queue.put(data)
            else:
                self.post(data)
        if user_threads:
            queue.join()
        logger.info("Complete")


if __name__ == "__main__":
    spamer = Spamer(
        url="http://localhost:8000/api/v1/films/film-timestamp/", n_films=1000, n_users=1000, n_workers=10, n_posts=100
    )
    spamer.spam(user_threads=True)
