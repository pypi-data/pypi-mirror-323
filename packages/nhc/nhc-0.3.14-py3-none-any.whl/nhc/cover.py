from .action import NHCAction
from .const import COVER_OPEN, COVER_CLOSE, COVER_STOP

class NHCCover(NHCAction):
    def __init__(self, controller, action):
        super().__init__(controller, action)

    @property
    def is_open(self) -> bool:
        return self._state > 0

    def open(self) -> None:
        self._controller.execute(self.id, COVER_OPEN)

    def close(self) -> None:
        self._controller.execute(self.id, COVER_CLOSE)

    def stop(self) -> None:
        self._controller.execute(self.id, COVER_STOP)
