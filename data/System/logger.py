import logging
import os

# Настройка логирования
base_dir = os.getcwd()
logs_folder = os.path.join(base_dir, "data", "System", "logs")
os.makedirs(logs_folder, exist_ok=True)

# Путь к файлу логов
log_file = os.path.join(logs_folder, "SuperApp.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=log_file,
    filemode="a",  # append
)

def log_event(message):
    logging.info(message)
