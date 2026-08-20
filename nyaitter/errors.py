import aiohttp
from typing import Optional
class HTTPException(Exception):
    def __init__(self, response: Optional[aiohttp.ClientResponse], data):
        self.response = response
        self.data = data

        if response is None:
            self.status = None
            msg = f"HTTP request failed: {data}"
        else:
            self.status = response.status
            msg = f"HTTP {self.status}: {data}"

        super().__init__(msg)


class NotFound(HTTPException):
    pass
class Forbidden(HTTPException):
    pass
class Unauthorized(HTTPException):
    pass
class RateLimited(HTTPException):
    pass