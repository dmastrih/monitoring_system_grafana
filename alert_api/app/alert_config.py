import logging
import os


class AlertConfig:

    def __init__(self, log_dir="logs", log_level="DEBUG"):
        self.log_dir = log_dir
        self.log_level = log_level
        self._setup_logger()

    def _setup_logger(self):
        os.makedirs(self.log_dir, exist_ok=True)

        self.logger = logging.getLogger("alert_api")
        self.logger.setLevel(getattr(logging, self.log_level.upper()))

        self.logger.handlers.clear()

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        log_file = os.path.join(self.log_dir, "alert_api.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

    def log_alert(self, level, message, alert_type="system"):
        level_functions = {
            'debug': self.logger.debug,
            'info': self.logger.info,
            'warning': self.logger.warning,
            'error': self.logger.error,
            'critical': self.logger.critical,
        }

        if level.lower() in level_functions:
            alert_message = f"[{alert_type.upper()}] {message}"
            level_functions[level.lower()](alert_message)
        else:
            self.logger.warning(f"Неизвестный уровень логирования: {level}")


alert_config = AlertConfig()
logger = alert_config.get_logger()
