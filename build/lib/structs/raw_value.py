from json import JSONEncoder
from typing import Any


class RawValue:

    _value: str = None

    def __init__(self, value):
        self._value = value
    
    def __str__(self):
        return self._value

class RawValueAwareEncoder(JSONEncoder):

    def default(self, o: Any) -> Any:
        if(isinstance(o, RawValue)):
            return str(RawValue)
        return super().default(o)
    