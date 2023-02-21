from io import TextIOWrapper
from typing import Any
from interfaces.text_writer import TextWriter
from structs.global_metadata import GlobalMetadata

from writers.sql_insert_writer import SqlInsertWriter

class SqlFileWriter(TextWriter):

    _metadata: GlobalMetadata = None
    _truncate: bool = False
    _resolution_context: dict[str, list[dict[str, Any]]] = None

    def __init__(self, metadata: GlobalMetadata, truncate: bool, resolution_context: dict[str, list[dict[str, Any]]]):
        self._metadata = metadata
        self._truncate = truncate
        self._resolution_context = resolution_context

    def write(self, stream: TextIOWrapper):
        # Write Pre-SQL
        stream.writelines([f'{sql}\n' for sql in self._metadata.get_metadata_entry('pre_sql')])

        # Write Truncates
        if(self._truncate):
            for doc in reversed(self._resolution_context.keys()):
                stream.write(f'TRUNCATE {doc} CASCADE;\n')
        
        # Write Post-Truncate SQL
        stream.writelines(f'{sql}\n' for sql in self._metadata.get_metadata_entry('after_truncate_sql'))

        # Write Inserts
        for doc, entries in self._resolution_context.items():
            if(len(entries) > 0):
                SqlInsertWriter(doc, entries).write(stream)
        
        # Write Post-Insert SQL
        stream.writelines(f'{sql}\n' for sql in self._metadata.get_metadata_entry('post_sql'))