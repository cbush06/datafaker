import random
from types import MappingProxyType
from typing import Any

from faker import Faker

from structs.document_metadata import DocumentMetadata


class DocumentContext:
    def get_doc_name(self) -> str:
        pass

    def get_document(self) -> MappingProxyType:
        pass

    def one_of_doc(self, key: str) -> Any:
        pass
    
    def one_of_sql(self, query: str) -> Any:
        pass

    def sql(self, query: str) -> Any:
        pass

    def sequence(self, field_name, start, step) -> int:
        pass

    def fake(self) -> Faker:
        pass
    
    def get_random(self) -> random.Random:
        pass
    
    def get_metadata(self) -> DocumentMetadata:
        pass