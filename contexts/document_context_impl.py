from itertools import product
import random
from types import MappingProxyType
from typing import Any
from faker import Faker
from sqlalchemy import engine, text
from structs.document_metadata import CardinalityIndicator, DocumentMetadata
from interfaces.document_context import DocumentContext
from contexts.record_context_impl import RecordContextImpl
from structs.from_doc import FromDoc
from structs.from_sql import FromSql
from structs.many_to_many import ManyToMany, SourceType
from structs.sequence import Sequence
from utils.db import safe_engine_call

class DocumentContextImpl(DocumentContext):

    _cache: dict[str, any] = None
    _eng: engine.Engine = None
    _metadata: DocumentMetadata = None
    _sequences: dict[str, Sequence] = None
    _doc_name: str = None
    _doc: dict[str, any] = None
    _resolution_context: dict[str, list[dict[str, Any]]] = None
    _fake: Faker = None
    _random: random.Random = None
    
    def __init__(self, cache: dict[str, Any], eng: engine.Engine, doc_name: str, doc: dict[str, any], resolution_context: dict[str, list[dict[str, Any]]], fake: Faker, random: random.Random):
        self._cache = cache
        self._eng = eng
        self._metadata = DocumentMetadata(doc_name, doc)
        self._sequences: dict[str, Sequence] = dict()
        self._doc_name = doc_name
        self._doc = doc
        self._resolution_context = resolution_context
        self._fake = fake
        self._random = random
    
    def resolve(self):
        data: list[dict[str, any]] = []

        # Create records based on the cardinality indicator defined
        cardinality_indicator = self._metadata.get_cardinality_indicator()

        # Create COUNT number of records
        if cardinality_indicator == CardinalityIndicator.COUNT:
            for i in range(self._metadata.get_metadata_entry('count')):
                data.append(RecordContextImpl(self).get_resovled())
        
        # Create a record for each SQL result
        elif cardinality_indicator == CardinalityIndicator.SQL:
            from_sql: FromSql = self._metadata.get_metadata_entry('from_sql')

            with safe_engine_call(self._eng).connect() as conn:
                for record in conn.execute(text(from_sql.get_sql())):
                    if(from_sql.filter(record)):
                        for x in range(from_sql.get_multiply()):
                            if(len(data) >= from_sql.get_limit()):
                                return data
                            data.append(RecordContextImpl(self, record, x).get_resovled())
        
        # Create a record for each DOC entry
        elif cardinality_indicator == CardinalityIndicator.DOC:
            from_doc: FromDoc = self._metadata.get_metadata_entry('from_doc')

            if(from_doc.get_doc_name() not in self._resolution_context):
                raise ValueError(f"Value for {self._doc_name}._from_doc.doc_name is invalid -- it must be a document defined above {self._doc_name}")

            for entry in self._resolution_context[from_doc.get_doc_name()]:
                if(from_doc.filter(entry)):
                    for x in range(from_doc.get_multiply()):
                        if(len(data) >= from_doc.get_limit()):
                            return data
                        data.append(RecordContextImpl(self, entry, x).get_resovled())
        
        # Create a record for a many-to-many join
        elif cardinality_indicator == CardinalityIndicator.MANY:
            many_to_many: ManyToMany = self._metadata.get_metadata_entry('many_to_many')
            left: list[any] = []
            right: list[any] = []

            # Get left source
            if(many_to_many.get_left_type() == SourceType.DOC):
                if(many_to_many.get_left_doc() not in self._resolution_context):
                    raise ValueError(f"Value for {self._doc_name}._many_to_many.left_doc is invalid -- it must be a document defined above {self._doc_name}")
                left = self._resolution_context[many_to_many.get_left_doc()]
            else:
                with safe_engine_call(self._eng).connect() as conn:
                    left = next(conn.execute().partitions())
            
            # Get right source
            if(many_to_many.get_right_type() == SourceType.DOC):
                if(many_to_many.get_right_doc() not in self._resolution_context):
                    raise ValueError(f"Value for {self._doc_name}._many_to_many.right_doc is invalid -- it must be a document defined above {self._doc_name}")
                right = self._resolution_context[many_to_many.get_right_doc()]
            else:
                with safe_engine_call(self._eng).connect() as conn:
                    right = next(conn.execute().partitions())
            
            # Produce records from the cartesian product
            for (left_context, right_context) in product(left, right):
                # Stay under a defined limit
                if many_to_many.get_limit() != None and many_to_many.get_limit() <= len(data):
                    break

                # Apply filters
                if many_to_many.filter_left(left_context) and many_to_many.filter_right(right_context):
                    data.append(RecordContextImpl(self, { 'left': left_context, 'right': right_context }).get_resovled())
        
        else: #EMPTY
            return []

        return data
    
    def get_doc_name(self):
        return self._doc_name
    
    def get_document(self):
        return MappingProxyType(self._doc)

    def one_of_doc(self, key: str):
        if(key not in self._cache):
            [doc, field] = key.split('.')
            self._cache[key] = list(entry[field] for entry in self._resolution_context[doc])
        
        if(len(self._cache[key]) == 0):
            return None

        return self._random.choice(self._cache[key])
    
    def one_of_sql(self, query: str):
        if(query not in self._cache):
            with safe_engine_call(self._eng).connect() as conn:
                self._cache[query] = list(row[0] for row in conn.execute(text(query)).all())
        
        if(len(self._cache[query]) == 0):
            return None

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
    
    def get_random(self):
        return self._random
    
    def get_metadata(self) -> DocumentMetadata:
        return self._metadata