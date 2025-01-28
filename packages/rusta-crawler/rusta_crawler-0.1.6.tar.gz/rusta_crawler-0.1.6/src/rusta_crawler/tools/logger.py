import logging
import os
import datetime
__name__ = "Rusta Crawler"
# Configure logging

from pathlib import Path

home = home = os.path.expanduser("~")

log_dir = os.path.join(home, "rusta_logs")

try:
    os.makedirs(log_dir, exist_ok=True)
except Exception as e:
    print(f"Error creating log directory: {e}")
    SystemExit(1)

log_file = os.path.join(log_dir, f"spider log {datetime.date.today().strftime('%Y-%m-%d')}.log")
log_file_core_engine = os.path.join(log_dir, f"core engine log {datetime.date.today().strftime('%Y-%m-%d')}.log")
try:
    log = logging.getLogger(__name__)
    fh = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(asctime)s: %(levelname)s: %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    fh.setLevel(logging.INFO)
    log.addHandler(fh)

    logging.basicConfig(
        filename=log_file_core_engine, format="%(levelname)s: %(message)s", level=logging.ERROR
    )

   
except Exception as e:
    print(f"Error setting up logging: {e}")



def log_info(text):
    log.info(f'{text}')

def log_error(text):
    log.error(f'{text}')

def log_warning(text):
    log.warning(f'{text}')