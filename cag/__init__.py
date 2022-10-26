import logging
from pathlib import Path
__version__ = "0.23.0"

logs_folder = '~/cag_logs'
Path(logs_folder).mkdir(parents=True, exist_ok=True)

# Create a custom logger
global logger
logger = logging.getLogger(__name__)

# Create handlers
console_handler = logging.StreamHandler()
#console_handler.setLevel(logging.INFO)
console_format = logging.Formatter('%(name)-12s %(levelname)-8s %(message)s')
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)


f_handler = logging.FileHandler("{}/logs.txt".format( logs_folder))
#f_handler.setLevel(logging.INFO)
file_format = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%d.%m.%Y %H:%M')
f_handler.setFormatter(file_format)
logger.addHandler(f_handler)

logger.setLevel(logging.INFO)






