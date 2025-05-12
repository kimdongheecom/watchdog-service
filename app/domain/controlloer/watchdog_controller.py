
from app.domain.service.watchdog_service import WatchdogService


class WatchdogController:
    def __init__(self):
        self.watchdog_service = WatchdogService()

    def preprocess(self):
        return self.watchdog_service.preprocess()
