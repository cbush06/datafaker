from typing import Any
from structs.field import Field
from contexts.field_context_impl import FieldContextImpl
from interfaces.document_context import DocumentContext
from interfaces.record_context import RecordContext
from utils.path import walk_path_for_value

class RecordContextImpl(RecordContext):
    _document_context: DocumentContext = None
    _from_context: dict[str, Any] = None
    _record: dict[str, Field] = None
    _multiply_idx: int = None

    def __init__(self, document_context: DocumentContext, from_context: dict[str, Any] = None, multiply_idx: int = 1):
        self._document_context = document_context
        self._from_context = from_context
        self._record = dict()
        self._multiply_idx = multiply_idx

        # Load this record with unresolved field values
        for key, value in document_context.get_document().items():
            if(key[:1] == '_'): # Ignore meta data
                continue
            self._record[key] = Field(value)
    
    def get_resovled(self):
        return { name: self.field(name) for name in self._record }
    
    def field(self, name):
        if(not self._record[name].is_resolved()):
            self._record[name].set_value(self._resolve_field(name))
        return self._record[name].get_value()
    
    def from_field(self, name):
        if(self._from_context == None):
            raise ValueError(f"from_field('{name}') was called when neither _from_sql nor _from_doc were provided")
        return walk_path_for_value(self._document_context.get_doc_name(), name, self._from_context)
    
    def fake(self):
        return self._document_context.fake()

    def get_multiply_idx(self):
        return self._multiply_idx

    def _resolve_field(self, name):
        input = self._record[name].get_value()
        if(isinstance(input, str)):
            return eval(self._record[name].get_value(), FieldContextImpl(name, self._document_context, self).to_global())
        return input