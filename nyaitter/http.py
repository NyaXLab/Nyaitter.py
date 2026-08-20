import asyncio
import aiohttp
from urllib.parse import quote as _uriquote
import sys

from typing import (
    ClassVar,
    Dict,
    Optional,
    Union
)

from . import __version__

from .errors import (
    HTTPException,
    NotFound,
    Forbidden,
    Unauthorized,
    RateLimited
)

from .utils import (
    _from_json,
    _to_json,
    Any,
    MISSING
)


class Route:
    BASE: ClassVar[str] = 'https://api.nyaitter.jp'

    def __init__(
        self,
        method: str,
        path: str,
        *,
        metadata: Optional[str] = None,
        **parameters: Any
    ) -> None:
        self.method = method
        self.path = path
        self.metadata = metadata
        self.parameters = parameters

        # パラメータを URL に埋め込む
        url = self.BASE + self.path
        if parameters:
            url = url.format_map({
                k: _uriquote(v, safe='') if isinstance(v, str) else v
                for k, v in parameters.items()
            })

        self.url = url

        # よく使う ID を保持
        self.user_id = parameters.get('user_id')
        self.post_id = parameters.get('post_id')
        self.dm_id = parameters.get('dm_id')

    @property
    def key(self) -> str:
        if self.metadata:
            return f'{self.method} {self.path}:{self.metadata}'
        return f'{self.method} {self.path}'

    @property
    def major_parameters(self) -> str:
        return '+'.join(
            str(k) for k in (self.post_id, self.user_id, self.dm_id) if k is not None
        )

async def json_or_text(response: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
    text = await response.text(encoding='utf-8')
    try:
        if response.headers['content-type'].split(';', 1)[0].strip() == 'application/json':
            return _from_json(text)
    except KeyError:
        pass
    return text

class HTTPClient:
    def __init__(self):
        self.loop = None
        self.connector = None
        self.__session = None
        self.user_agent = f'Nyaitter.py ({__version__}) Python/{sys.version_info[0]}.{sys.version_info[1]} aiohttp/{aiohttp.__version__}'
        self.token = None

    def setup(self, loop, connector=None):
        self.loop = loop
        self.connector = connector or aiohttp.TCPConnector()
        self.__session = aiohttp.ClientSession(connector=self.connector)

    async def close(self) -> None:
        if not self.__session.closed:
            await self.__session.close()

    async def request(
        self,
        route: Route,
        *,
        json: Optional[Dict[str, Any]] = {},
        **kwargs: Any
    ) -> Any:
        method = route.method
        url = route.url

        # ---- JSON 専用ヘッダ ----
        headers: Dict[str, str] = {
            'User-Agent': self.user_agent,
            'Content-Type': 'application/json'
        }

        if self.token is not None:
            headers['Authorization'] = 'Bearer ' + self.token

        # ---- JSON 以外は禁止 ----
        if json is None:
            raise TypeError("This API requires JSON for all requests.")

        # JSON を data に変換
        kwargs['data'] = _to_json(json)
        kwargs['headers'] = headers

        # ---- 再試行つき HTTP リクエスト ----
        for tries in range(5):
            async with self.__session.request(method, url, **kwargs) as response:
                data = await json_or_text(response)

                match response.status:
                    case 200 | 201 | 204:
                        return data

                    case 429:
                        retry_after = float(response.headers.get("Retry-After", "1"))
                        await asyncio.sleep(retry_after)
                        if tries == 4:
                            raise RateLimited(response, data)
                        continue

                    case 404:
                        raise NotFound(response, data)

                    case 403:
                        raise Forbidden(response, data)

                    case 401:
                        raise Unauthorized(response, data)

                    case _ if 400 <= response.status < 600:
                        raise HTTPException(response, data)

                    case _:
                        return data

        raise HTTPException(None, "Too many retries")



