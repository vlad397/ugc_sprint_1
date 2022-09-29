import os
from logging import config as logging_config

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


DEBUG = os.getenv("DEBUG", "False") == "True"
API_VERSION = "v1"
JWT_SECRET = "qwerty"
# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv("PROJECT_NAME", "ugc_api")

KAFKA_HOST = os.getenv("KAFKA_HOST", "kafka")
KAFKA_PORT = os.getenv("KAFKA_PORT", 9092)


# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
