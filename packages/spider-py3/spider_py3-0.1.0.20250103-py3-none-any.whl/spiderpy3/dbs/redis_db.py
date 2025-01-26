import redis
from typing import Any

from spiderpy3.dbs.db import DB


class RedisDB(DB):
    def __init__(
            self,
            *args: Any,
            **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

    def _open(self) -> None:
        pass

    def _close(self) -> None:
        pass
