import asyncio
import aiohttp
import inspect

from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    TypeVar
)

from .http import HTTPClient, Route

from .post import Post
from .user import User

EventFunc = TypeVar("EventFunc", bound=Callable[..., Any])

class Client:
    def __init__(self, token: str, loop: asyncio.AbstractEventLoop=None, connector:aiohttp.BaseConnector=None):
        self.loop: asyncio.AbstractEventLoop = loop
        self.connector: aiohttp.BaseConnector = connector
        self.http: HTTPClient = None
        self.token: str = token
        self.me: User = None
        self._events: Dict[str, Any] = {}

    def event(self, func: EventFunc) -> EventFunc:
        self._events[func.__name__] = func
        return func

    async def _dispatch(self, event_name:str, *args, **kwargs):
        func = self._events.get(event_name)
        if not func:
            return
        if inspect.iscoroutinefunction(func):
            await func(*args, **kwargs)
        else:
            func(*args, **kwargs)

    async def start(self):
        # /auth/me を叩く前に HTTPClient が初期化されている必要がある
        route = Route("GET", "/auth/me")
        me = await self.http.request(route)
        self.me = User.from_json(me, client=self)
        await self._dispatch("on_ready")

    def login(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.loop = loop

        # HTTPClient をここで初期化
        self.http = HTTPClient()
        self.http.token = self.token
        self.http.setup(loop, self.connector)

        try:
            loop.run_until_complete(self.start())
            loop.run_forever()
        finally:
            loop.run_until_complete(self.http.close())
            loop.close()

    async def close(self):
        await self.http.close()
        if self.loop.is_running():
            self.loop.stop()

    async def fetch_user(self, user_id: int):
        route = Route("GET", "/api/users/{user_id}", user_id=user_id)
        data = await self.http.request(route)
        return User.from_json(data, client=self)

    async def post(self, content:str, lock:Optional[bool] = False, mask:Optional[bool] = False) -> Post:
        route = Route("POST", "/api/posts")
        req = await self.http.request(route, json={
            "announcement": False,
            "attachments": [], #後で実装
            "content":content,
            "lock": lock,
            "mask": mask,
            "reply_to": None,
            "repost_to": None
        })
        post = Post.from_json(req, self)
        return post
