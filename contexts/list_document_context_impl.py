import random
from types import MappingProxyType
from typing import Any
from faker import Faker
from sqlalchemy import engine, text
from structs.document_metadata import DocumentMetadata
from interfaces.document_context import DocumentContext
from contexts.record_context_impl import RecordContextImpl
from structs.sequence import Sequence
from utils.db import safe_engine_call

class ListDocumentContextImpl(DocumentContext):

    _cache: dict[str, any] = None
    _eng: engine.Engine = None
    _metadata: DocumentMetadata = None
    _sequences: dict[str, Sequence] = None
    _list_name: str = None
    _doc: dict[str, any] = None
    _resolution_context: dict[str, list[dict[str, Any]]] = None
    _fake: Faker = None
    _random: random.Random = None
    
    def __init__(self, cache: dict[str, Any], eng: engine.Engine, list_name: str, doc: dict[str, any], resolution_context: dict[str, list[dict[str, Any]]], sequences: dict[str, Sequence], fake: Faker, random: random.Random):
        self._cache = cache
        self._eng = eng
        self._metadata = DocumentMetadata(list_name, doc)
        self._sequences = sequences
        self._list_name = list_name
        self._doc = doc
        self._resolution_context = resolution_context
        self._fake = fake
        self._random = random
    
    def resolve(self):
        return RecordContextImpl(self).get_resovled()
    
    def get_doc_name(self):
        return self._list_name
    
    def get_document(self):
        return MappingProxyType(self._doc)

    def one_of_doc(self, key: str):
        if(key not in self._cache):
            [doc, field] = key.split('.')
            self._cache[key] = list(entry[field] for entry in self._resolution_context[doc])
        return self._random.choice(self._cache[key])
    
    def one_of_sql(self, query: str):
        if(query not in self._cache):
            with safe_engine_call(self._eng).connect() as conn:
                self._cache[query] = list(row[0] for row in conn.execute(text(query)).all())
        return self._random.choice(self._cache[query])
    
    def sql(self, query: str):
        with safe_engine_call(self._eng).connect() as conn:
            return conn.execute(query).first()[0]

    def sequence(self, field_name, start = 0, step = 1):
        if(field_name not in self._sequences):
            self._sequences[field_name] = Sequence(start, step)
        return self._sequences[field_name].next()

    def fake(self):
        return self._fake
    
    def get_random(self) -> random.Random:
        return self._random

    def get_metadata(self) -> DocumentMetadata:
        return self._metadata