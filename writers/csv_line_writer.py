import csv
from io import TextIOWrapper
from typing import Any

from interfaces.text_writer import TextWriter


class CsvLineWriter(TextWriter):

    _entries: list[dict[str, Any]] = None
    _columns: list[str] = None

    def __init__(self, entries: list[dict[str, Any]]):
        self._entries = entries
        self._columns = list(entries[0].keys())
    
    def write(self, stream: TextIOWrapper):
            writer = csv.DictWriter(stream, fieldnames=self._columns)
            writer.writeheader()
            { writer.writerow(entry) for entry in self._entries }