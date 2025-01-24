from dataclasses import dataclass
from types import TracebackType
from typing import Any, Callable

import requests
from aiohttp import ClientSession
from requests import Session


@dataclass
class Api:
    Url: str
    Method: str
    ContentType: str


class HttpMethod:
    Get: str = 'GET'
    Post: str = 'POST'
    Options: str = 'OPTIONS'
    Put: str = 'PUT'
    Delete: str = 'DELETE'


class Requester:
    def __init__(self, timeout: int = 30):
        self.__session: Session | None = None
        self.__timeout: int = timeout

    def __enter__(self):
        self.__session = requests.session()
        return self

    def __exit__(self,
                 exc_type: type[BaseException] | None,
                 exc_val: BaseException | None,
                 exc_tb: TracebackType | None):
        if (self.__session):
            self.__session.close()

    def request(self,
                api: Api,
                params: dict | None = None,
                data: dict | None = None,
                json: dict | None = None,
                headers: dict | None = None,
                **kwargs) -> requests.Response | None:
        if not self.__session:
            return None

        headers = headers or dict()
        if api.ContentType:
            headers['Content-Type'] = api.ContentType
        return self.__session.request(api.Method,
                                      api.Url,
                                      params=params,
                                      data=data,
                                      json=json,
                                      headers=headers,
                                      timeout=self.__timeout,
                                      **kwargs)


class RequesterAsync:
    def __init__(self, session: ClientSession, proxy: str | None = None):
        self.__session: ClientSession = session
        self.__proxy: str | None = proxy

    async def request(self,
                      api: Api,
                      params: dict | None = None,
                      data: dict | None = None,
                      json: dict | None = None,
                      headers: dict | None = None,
                      **kwargs) -> tuple[Any, int]:
        if not self.__session:
            return None, -1

        headers = headers or dict()
        if api.ContentType:
            headers['Content-Type'] = api.ContentType
        method: Callable = self.__session.get
        match api.Method:
            case HttpMethod.Post:
                method = self.__session.post
            case HttpMethod.Options:
                method = self.__session.options
            case HttpMethod.Put:
                method = self.__session.put
            case HttpMethod.Delete:
                method = self.__session.delete
            case _:
                raise ValueError(f'Invalid method: {api.Method}')

        async with method(api.Url,
                          params=params,
                          data=data,
                          json=json,
                          headers=headers,
                          proxy=self.__proxy,
                          **kwargs) as response:
            return await response.json(), response.status
