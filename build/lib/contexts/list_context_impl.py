import random
from typing import Any
from faker import Faker
from sqlalchemy import engine
from interfaces.list_context import ListContext
from contexts.list_document_context_impl import ListDocumentContextImpl
from contexts.record_context_impl import RecordContextImpl
from structs.sequence import Sequence


class ListContextImpl(ListContext):

    _cache: dict[str, any] = None
    _eng: engine.Engine = None
    _sequences: dict[str, Sequence] = None
    _list_name: str = None
    _list: dict[str, any] = None
    _resolution_context: dict[str, list[dict[str, Any]]] = None
    _fake: Faker = None
    _random: random.Random = None
    
    def __init__(self, cache: dict[str, Any], eng: engine.Engine, list_name: str, list: list[dict[str, any]], resolution_context: dict[str, list[dict[str, Any]]], fake: Faker, random: random.Random):
        self._cache = cache
        self._eng = eng
        self._sequences: dict[str, Sequence] = dict()
        self._list_name = list_name
        self._list = list
        self._resolution_context = resolution_context
        self._fake = fake
        self._random = random
    
    def resolve(self):
        data: list[dict[str, any]] = []

        for next_doc in self._list:
            data.append(RecordContextImpl(ListDocumentContextImpl(self._cache, self._eng, self._list_name, next_doc, self._resolution_context, self._sequences, self._fake, self._random)).get_resovled())
        
        return data