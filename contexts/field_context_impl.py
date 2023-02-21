from datetime import datetime, timedelta
from typing import Any
from interfaces.document_context import DocumentContext
from interfaces.field_context import FieldContext
from interfaces.record_context import RecordContext
from structs.raw_value import RawValue


class FieldContextImpl(FieldContext):

    _field_name: str = None
    _document_context: DocumentContext = None
    _record_context: RecordContext = None

    def __init__(self, field_name: str, document_context: DocumentContext, record_context: RecordContext):
        self._field_name = field_name
        self._document_context = document_context
        self._record_context = record_context
    
    def sequence(self, start = 0, step = 1):
        return self._document_context.sequence(self._field_name, start, step)
    
    def first_name(self):
        return self._record_context.fake().first_name()
    
    def last_name(self):
        return self._record_context.fake().last_name()
    
    def random_char(self):
        return chr(self._document_context.get_random().randint(65, 90))

    def random_int(self, min = 0, max = 10):
        return self._document_context.get_random().randint(min, max)

    def digits(self, length):
        max = 10**length - 1
        return str(self._document_context.get_random().randint(0, max)).zfill(length)
    
    def one_of_doc(self, key: str):
        return self._document_context.one_of_doc(key)
    
    def one_of_sql(self, query: str):
        return self._document_context.one_of_sql(query)
    
    def sql(self, query: str):
        return self._document_context.sql(query)
    
    def one_of(self, options: list):
        return self._document_context.get_random().choice(options)
    
    def field(self, name: str):
        return self._record_context.field(name)
    
    def fromisoformat(self, input: str):
        return datetime.fromisoformat(input)
    
    def now(self):
        return datetime.now()
    
    def milliseconds(self, delta: int):
        return timedelta(0, 0, 0, delta)
    
    def seconds(self, delta: int):
        return timedelta(0, delta)
    
    def minutes(self, delta: int):
        return timedelta(0, 0, 0, 0, delta)
    
    def hours(self, delta: int):
        return timedelta(0, 0, 0, 0, 0, delta)
    
    def days(self, delta: int):
        return timedelta(delta)
    
    def integer(self, value: Any):
        return int(value)
    
    def floating(self, value: Any):
        return float(value)
    
    def boolean(self, value: Any):
        return bool(value)
    
    def string(self, value: Any):
        return str(value)
    
    def upper(self, value: str):
        return value.upper()
    
    def lower(self, value: str):
        return value.lower()
    
    def raw(self, value: str):
        return RawValue(value)
    
    def to_global(self):
        return {
            'fake': self._record_context.fake()['en-US'],
            'sequence': self.sequence,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'random_char': self.random_char,
            'random_int': self.random_int,
            'digits': self.digits,
            'one_of_doc': self.one_of_doc,
            'one_of_sql': self.one_of_sql,
            'sql': self.sql,
            'one_of': self.one_of,
            'field': self.field,
            'from_field': self._record_context.from_field,
            'fromisoformat': self.fromisoformat,
            'now': self.now,
            'milliseconds': self.milliseconds,
            'seconds': self.seconds,
            'minutes': self.minutes,
            'hours': self.hours,
            'days': self.days,
            'integer': self.integer,
            'floating': self.floating,
            'boolean': self.boolean,
            'string': self.string,
            'upper': self.upper,
            'lower': self.lower,
            'raw': self.raw,
            'multiply_idx': self._record_context.get_multiply_idx
        }