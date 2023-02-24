import os

from cag.utils.config import Config

config = Config(
    url=f"http://{os.environ['API_USER']}:{os.environ['ARANGO_PORT']}",
    user="",
    password="",
    graph="SampleGraph",
    database="test"
)
