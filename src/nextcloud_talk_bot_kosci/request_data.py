import json
from typing import Dict, Any


class RequestData:
    def __init__(self, raw):
        self.raw = raw

    def __getattr__(self, item):
        return self._get_value(item)

    def __getitem__(self, item):
        return self._get_value(item)

    def _get_value(self, item):
        if item == 'content':
            return json.loads(self.raw['object']['content'])
        if item == 'message':
            return json.loads(self.raw['object']['content'])['message']

        return self.raw[item] if item in self.raw else None

    def __repr__(self):
        return self.raw

    def __str__(self):
        return json.dumps(self.raw)
