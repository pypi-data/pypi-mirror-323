"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from requests.adapters import HTTPAdapter

from tap_api.v2.endpoints import *
from tap_api.web.error_handler import ErrorHandler
from tap_api.web.resource import Resource


class TimeoutHTTPAdapter(HTTPAdapter):
    timeout = None

    def __init__(self, *args, **kwargs):
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None and hasattr(self, 'timeout'):
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


class Client(Resource):
    __api_token: str
    __error_handler: ErrorHandler
    __forensics: Forensics
    __campaign: Campaign
    __people: People
    __threat: Threat
    __siem: Siem
    __url: Url

    def __init__(self, principal: str, secret: str):
        super().__init__(None, 'https://tap-api-v2.proofpoint.com/v2')
        self.__error_handler = ErrorHandler()
        self._session.hooks = {"response": self.__error_handler.handler}
        self._session.auth = (principal, secret)
        self.__siem = Siem(self, 'siem')
        self.__forensics = Forensics(self, 'forensics')
        self.__campaign = Campaign(self, 'campaign')
        self.__people = People(self, 'people')
        self.__threat = Threat(self, 'threat')
        self.__siem = Siem(self, 'siem')
        self.__url = Url(self, 'url')

    @property
    def forensics(self) -> Forensics:
        return self.__forensics

    @property
    def campaign(self) -> Campaign:
        return self.__campaign

    @property
    def people(self) -> People:
        return self.__people

    @property
    def threat(self) -> Threat:
        return self.__threat

    @property
    def url(self) -> Url:
        return self.__url

    @property
    def siem(self) -> Siem:
        return self.__siem

    @property
    def siem(self) -> Siem:
        return self.__siem

    @property
    def timeout(self):
        return self._session.adapters.get('https://').timeout

    @timeout.setter
    def timeout(self, timeout):
        self._session.adapters.get('https://').timeout = timeout

    @property
    def error_handler(self) -> ErrorHandler:
        return self.__error_handler

    @error_handler.setter
    def error_handler(self, error_handler: ErrorHandler):
        self.__error_handler = error_handler
