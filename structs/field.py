from typing import Any


class Field:
    _is_resolved: bool = False
    _value: Any = None

    def __init__(self, value):
        self._is_resolved = False
        self._value = value
    
    def is_resolved(self):
        return self._is_resolved

    def set_value(self, value):
        self._is_resolved = True
        self._value = value
    
    def get_value(self):
        return self._value
