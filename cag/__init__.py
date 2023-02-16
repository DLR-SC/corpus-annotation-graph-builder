import logging
from pathlib import Path

__version__ = "1.3.0"

logs_folder_name = "cag_logs"
# User home dir detection. Linux and Windows compatible
home_directory = Path.home()
logs_folder = home_directory.joinpath(logs_folder_name)
if not logs_folder.exists():
    logs_folder.mkdir()

# Create a custom logger
global logger
logger = logging.getLogger(__name__)

# Create handlers
console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)
console_format = logging.Formatter("%(name)-12s %(levelname)-8s %(message)s")
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)

f_handler = logging.FileHandler(f"{logs_folder}/logs.txt")
# f_handler.setLevel(logging.INFO)
file_format = logging.Formatter(
    "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%d.%m.%Y %H:%M",
)
f_handler.setFormatter(file_format)
logger.addHandler(f_handler)

logger.setLevel(logging.INFO)
