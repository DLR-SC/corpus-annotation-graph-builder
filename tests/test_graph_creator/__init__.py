from cag.utils.config import Config
from tests.test_nodes import whoami

config = Config(
    url="http://arangodb:8529",
    user="root",
    password="secret",
    graph="SampleGraph",
    database="test"
)
