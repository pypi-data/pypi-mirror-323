"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import Optional

from tap_api.common.filters import TimeWindow
from tap_api.web import FilterOptions
from tap_api.web.resource import Resource
from .vap_summary import VapSummary


class Vap(Resource):
    def __init__(self, parent, uri: str):
        super().__init__(parent, uri)

    def __call__(self, window: TimeWindow = TimeWindow.DAYS_30, page: Optional[int] = None,
                 size: Optional[int] = None) -> VapSummary:
        if not isinstance(window, TimeWindow):
            raise TypeError("`window` must be an instance of TimeWindow.")
        if page is not None and page < 1:
            raise ValueError("`page` must be 1 or greater.")
        if size is not None and size < 1:
            raise ValueError("`size` must be 1 or greater.")

        options = FilterOptions()
        options.add_option("window", window)
        options.add_option("page", page)
        options.add_option("size", size)

        return VapSummary(self._session.get(self._uri, params=options.params))
