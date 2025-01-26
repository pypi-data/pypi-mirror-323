import atexit
from DrissionPage import ChromiumPage
from DrissionPage.items import ChromiumTab
from typing import Any, Optional, Union, Dict, Literal


class DpMixin(object):
    def __init__(
            self,
            *args: Any,
            cp_kwargs: Optional[Dict[str, Any]] = None,
            ct_kwargs: Optional[Dict[str, Any]] = None,
            mode: Literal["cp", "ct"] = "ct",
            dp: Union[None, ChromiumTab, ChromiumPage] = None,
            close_dp: bool = True,
            **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

        self.cp_kwargs = dict(
            addr_or_opts=None,
            tab_id=None
        )
        if cp_kwargs is not None:
            self.cp_kwargs.update(cp_kwargs)

        self.ct_kwargs = dict(
            url=None,
            new_window=False,
            background=False,
            new_context=False
        )
        if ct_kwargs is not None:
            self.ct_kwargs.update(ct_kwargs)

        self.mode = mode

        self._dp = dp

        self.close_dp = close_dp

        atexit.register(self.close)

    @staticmethod
    def create_cp(**kwargs: Dict[str, Any]) -> ChromiumPage:
        cp = ChromiumPage(**kwargs)
        return cp

    @staticmethod
    def create_ct(cp: ChromiumPage, **kwargs: Dict[str, Any]) -> ChromiumTab:
        ct = cp.new_tab(**kwargs)
        return ct

    @property
    def dp(self) -> Union[ChromiumPage, ChromiumTab]:
        if self._dp is None:
            if self.mode == "cp":
                self._dp = self.create_cp(**self.cp_kwargs)
            elif self.mode == "ct":
                cp = self.create_cp(**self.cp_kwargs)
                self._dp = self.create_ct(cp, **self.ct_kwargs)
        return self._dp

    def close(self) -> None:
        if self.close_dp is True and self._dp is not None:
            if isinstance(self._dp, ChromiumPage):
                self._dp.close()
                self._dp.quit()
            elif isinstance(self._dp, ChromiumTab):
                self._dp.close()
