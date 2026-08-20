from typing import Any
import json
try:
    import orjson # type: ignore
except ModuleNotFoundError:
    HAS_ORJSON = False
else:
    HAS_ORJSON = True

class _MissingSentinel:
    __slots__ = ()

    def __eq__(self, other) -> bool:
        return False
    def __bool__(self) -> bool:
        return False
    def __hash__(self) -> int:
        return 0
    def __repr__(self):
        return '...'

MISSING:Any = _MissingSentinel()

if HAS_ORJSON:
    def _to_json(obj: Any) -> str:
        return orjson.dumps(obj).decode('utf-8')

    _from_json = orjson.loads # type: ignore
else:
    def _to_json(obj: Any) -> str:
        return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)

    _from_json = json.loads