from typing import Any, Callable


class GlobalMetadata:

    _metadata: dict[str, Any] = None

    _validators: dict[str, Callable[[any], bool]] = {
        'seed': lambda _, val: isinstance(val, int) and val > 0,
        'pre_sql': lambda _, val: isinstance(val, list) and len(val) > 0 and isinstance(val[0], str),
        'after_truncate_sql': lambda _, val: isinstance(val, list) and len(val) > 0 and isinstance(val[0], str),
        'post_sql': lambda _, val: isinstance(val, list) and len(val) > 0 and isinstance(val[0], str),
    }

    def __init__(self, schema: dict[str, any]):
        self._metadata = {
            'seed': None,
            'pre_sql': list(),
            'after_truncate_sql': list(),
            'post_sql': list(),
        }

        for key in schema:
            if(key[:1] == '_'):
                self._extract_metadata_entry(key[1:], schema[key])

    def _extract_metadata_entry(self, key: str, entry):
        if(key in self._metadata):
            if(self._validators[key](self, entry)):
                self._metadata[key] = entry
            else:
                raise ValueError(f"Value for schema._{key} is invalid")
        else:
            raise ValueError(f"Metadata entry _{key} is not recognized")
    
    def get_metadata_entry(self, key):
        return self._metadata[key]