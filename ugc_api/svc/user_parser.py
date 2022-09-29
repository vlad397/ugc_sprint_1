import abc
import uuid
from abc import ABC

import jwt
from core.config import JWT_SECRET


class UserParser(ABC):
    @abc.abstractmethod
    def get_user(self, *args, **kwargs) -> uuid.UUID:
        pass


class JWTUserParser(UserParser):
    def get_user(self, jwt_token: str) -> uuid.UUID:
        data = jwt.decode(jwt_token, JWT_SECRET, algorithms=["HS256"])
        return data["user_id"]
