import atexit
from typing import Any, Optional
from DrissionPage import ChromiumPage, ChromiumOptions


class DpMixin(object):
    def __init__(self,
                 *args: Any,
                 co: Optional[ChromiumOptions] = None,
                 cp: Optional[ChromiumPage] = None,
                 close_cp: bool = True,
                 **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        if co is None:
            co = self.create_co()
        self.co = co

        self._cp = cp
        self.close_cp = close_cp

        atexit.register(self.close)

    @staticmethod
    def create_co() -> ChromiumOptions:
        co = ChromiumOptions()
        return co

    @staticmethod
    def create_cp(co: ChromiumOptions) -> ChromiumPage:
        cp = ChromiumPage(co)
        return cp

    @property
    def cp(self) -> ChromiumPage:
        if self._cp is None:
            self._cp = self.create_cp(self.co)
        return self._cp

    def close(self) -> None:
        if self.close_cp is True and self._cp is not None:
            self._cp.quit()
        self.co = None
        self._cp = None
        self.close_cp = True

    def wait_complete(self, cp: Optional[ChromiumPage] = None) -> None:
        if cp is None:
            cp = self.cp
        while True:
            if cp.states.ready_state == "complete":
                break
