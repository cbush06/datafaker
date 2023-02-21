from datetime import datetime
from typing import Any
import click

from sqlalchemy import Boolean, Column, DateTime, MetaData, Numeric, String, Table, engine, literal, literal_column, text

from structs.raw_value import RawValue
from structs.schema import Schema


class DbWriter:

    _type_mappings: dict[type, type] = {
        str: String,
        int: Numeric,
        bool: Boolean,
        float: Numeric,
        RawValue: None,
        datetime: DateTime,
        type(None): None
    }
    _schema: Schema = None
    _resolution_context: dict[str, list[dict[str, Any]]] = None
    _truncate: bool = None
    _metadata: MetaData = None
    _tables: dict[str, Table] = None

    def __init__(self, schema: Schema, resolution_context: dict[str, list[dict[str,Any]]], truncate: bool):
        self._schema = schema
        self._resolution_context = resolution_context
        self._truncate = truncate
        self._metadata = MetaData()
        self._tables = dict()
    
    def _construct_tables(self):
        for doc, entries in self._resolution_context.items():
            columns = self._construct_columns(entries)
            self._tables[doc] = Table(doc, self._metadata, *columns)

    def _construct_columns(self, entries: list[dict[str, Any]]):
        columns: list[Column] = list()
        if(len(entries) > 0):
            for column, value in entries[0].items():
                if(column[:1] == '_'):
                    continue
                value_type = self._type_mappings[type(value)]
                columns.append(Column(column, value_type))
        return columns
    
    def write_db(self, eng: engine.Engine):
        if(len(self._tables) < 1):
            self._construct_tables()

        with eng.connect() as conn:
            # If we have pre-sql, run it
            for sql in self._schema.get_metadata_entry('pre_sql'):
                conn.execute(text(sql))

            # If we need to clear the tables first...
            if(self._truncate):
                for doc in reversed(self._resolution_context.keys()):
                    conn.execute(self._tables[doc].delete())
            
            # If we have after-truncate-sql, run it
            for sql in self._schema.get_metadata_entry('after_truncate_sql'):
                conn.execute(text(sql))
            
            # Now load the tables
            for doc in self._resolution_context.keys():
                new_records = self._resolution_context[doc]

                if(len(new_records) > 0):
                    conn.execute(
                        self._tables[doc].insert().values(
                            self._adapt_custom_types(new_records)
                        )
                    )
                else:
                    click.echo(f'INFO: skipping writing of {doc} because no records were created for it')
            
            # If we have post-sql, run it
            for sql in self._schema.get_metadata_entry('post_sql'):
                conn.execute(text(sql))
    
    def _adapt_custom_types(self, doc: list[dict[str, Any]]):
        result: list[dict[str, Any]] = list()
        for entry in doc:
            # NOTE: This removes fields starting with _
            result.append({ k: self._safe_value(v) for (k, v) in entry.items() if k[:1] != '_' })
        return result
    
    def _safe_value(self, val: Any):
        output = val
        if(isinstance(output, RawValue)):
            output = literal_column(str(output))
        return output