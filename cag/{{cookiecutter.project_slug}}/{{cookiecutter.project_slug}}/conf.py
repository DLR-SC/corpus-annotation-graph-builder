import os

from cag.utils.config import Config

"""
The code uses the Config class from the `cag.utils.config` module to create a configuration object with various 
parameters for an ArangoDB instance. The parameters are sourced from environment variables, but have default values 
in case they are not defined.
"""

HOST = os.environ.get("ARANGO_HOST", "localhost")
PORT = os.environ.get("ARANGO_PORT", 40100)
USER = os.environ.get("ARANGO_USER", "root")
PASSWORD = os.environ.get("ARANGO_PASSWORD", "root")
GRAPH = os.environ.get("ARANGO_GRAPH", "SampleGraph")
DATABASE = os.environ.get("ARANGO_DATABASE", "sample_database")

config = Config(
    url=f"http://{HOST}:{PORT}",
    user=USER,
    password=PASSWORD,
    graph=GRAPH,
    database=DATABASE,
)
