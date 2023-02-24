import os

from cag.utils.config import Config

config = Config(
    url=f"http://{os.environ['ARANGO_HOST']}:{os.environ['ARANGO_PORT']}",
    user="root",
    password="",
    graph="SampleGraph",
    database="test"
)
