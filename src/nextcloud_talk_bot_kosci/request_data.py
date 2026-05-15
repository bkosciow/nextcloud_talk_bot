from typing import Dict, Any

import json


class RequestData:
    def __init__(self, raw: Dict[str, Any]):
        self.raw: Dict[str, Any] = raw

    def __getattr__(self, item: str) -> Any:
        return self._get_value(item)

    def __getitem__(self, item: str) -> Any:
        return self._get_value(item)

    def _get_value(self, item: str) -> Any:
        if item == 'content':
            return json.loads(self.raw['object']['content'])  # type: Dict[str, Any]
        if item == 'message':
            return json.loads(self.raw['object']['content'])['message']  # type: str

        return self.raw[item] if item in self.raw else None

    def __repr__(self) -> str:
        return json.dumps(self.raw)

    def __str__(self) -> str:
        return json.dumps(self.raw)
