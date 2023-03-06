import os
import random
import string
from typing import Union

from cag.utils.config import Config


def get_random_string(length: int = 8) -> str:
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


def config_factory(database: str = get_random_string()) -> Config:
    return Config(
        url=f"http://{os.environ['ARANGO_HOST']}:{os.environ['ARANGO_PORT']}",
        user="root",
        password="",
        graph="SampleGraph",
        database=database,
    )
