import datetime
from typing import Any

from structs.field import Field


class FieldContext:

    def sequence(self, start, step) -> int:
        pass

    def random_int(min = 0, max = 10):
        pass

    def digits(length) -> str:
        pass

    def one_of_doc(self, key: str) -> Any:
        pass

    def one_of_sql(self, query: str) -> Any:
        pass
    
    def one_of(self, options) -> Any:
        pass
    
    def field(self, name) -> Field:
        pass

    def now(self) -> datetime:
        pass
    
    def milliseconds(self, delta) -> datetime.timedelta:
        pass
    
    def seconds(self, delta) -> datetime.timedelta:
        pass
    
    def minutes(self, delta) -> datetime.timedelta:
        pass
    
    def hours(self, delta) -> datetime.timedelta:
        pass
    
    def days(self, delta) -> datetime.timedelta:
        pass

    def integer(self, value) -> int:
        pass
    
    def floating(self, value) -> float:
        pass
    
    def boolean(self, value) -> bool:
        pass

    def string(self, value) -> str:
        pass

    def to_global(self) -> dict:
        pass