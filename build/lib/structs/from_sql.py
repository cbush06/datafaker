import sys
from typing import Callable


class FromSql:
    _doc_name: str = None
    _metadata: dict[str, any] = None

    _validators: dict[str, Callable[[any], bool]] = {
        'limit': lambda _, val: val == None or (isinstance(val, int) and val > 0),
        'filter': lambda _, val: val == None or (isinstance(val, str) and len(val.strip()) > 0),
        'sql': lambda _, val: val != None and isinstance(val, str) and len(val.strip()) > 0,
        'multiply': lambda _, val: val != None and (isinstance(val, int) and val > 0)
    }

    def __init__(self, doc_name: str, from_sql: dict[str, any]):
        self._doc_name = doc_name
        self._metadata = {
            'limit': None,
            'filter': None,
            'sql': None,
            'multiply': None
        }

        for key in from_sql:
            self._extract_metadata_entry(key, from_sql[key])
    
    def _extract_metadata_entry(self, key: str, entry):
        if(key in self._metadata):
            if(self._validators[key](self, entry)):
                self._metadata[key] = entry
            else:
                raise ValueError(f"Value for {self._doc_name}._from_sql.{key} is invalid")
        else:
            raise ValueError(f"Metadata entry {self._doc_name}._from_sql.{key} is not recognized")
    
    def get_sql(self):
        return self._metadata['sql']
    
    def get_limit(self):
        return self._metadata['limit'] if self._metadata['limit'] != None else sys.maxsize
    
    def filter(self, context):
        return self._metadata['filter'] == None or eval(self._metadata['filter'], context)
    
    def get_multiply(self):
        return self._metadata['multiply'] if self._metadata['multiply'] != None else 1