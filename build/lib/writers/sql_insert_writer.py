from datetime import datetime
from functools import reduce
from io import TextIOWrapper
from typing import Any
from interfaces.text_writer import TextWriter

from structs.raw_value import RawValue


class SqlInsertWriter(TextWriter):

    _doc: str = None
    _entries: list[dict[str, Any]] = None
    _types: dict[str, type] = None
    _encoders = {
        str: lambda val: "'" + str(val).replace('\'', '\'\'') + "'",
        int: lambda val: str(val),
        bool: lambda val: 'TRUE' if bool(val) else 'FALSE',
        float: lambda val: str(val),
        RawValue: lambda val: str(val),
        datetime: lambda val: datetime(val).isoformat(),
        type(None): lambda val: 'NULL'
    }

    def __init__(self, doc: str, entries: list[dict[str, Any]]):
        self._doc = doc
        self._entries = entries
        if(len(entries) < 0):
            raise ValueError(f'Encountered document {doc} with no entries while trying to serialize to SQL')
        self._types = {k: type(v) for (k, v) in entries[0].items()}
    
    def _to_insert(self, entry: dict[str, Any]):
        columns = [k for k in entry.keys() if k[:1] != '_']
        values = list()

        # Encode the values
        for column in columns:
            value = entry[column]
            encoder = self._encoders[type(value)]
            values.append(encoder(value))
        
        return f'INSERT INTO {self._doc} ({",".join(columns)}) VALUES({",".join(values)});\n'

    def write(self, stream: TextIOWrapper):
        stream.writelines([self._to_insert(entry) for entry in self._entries])