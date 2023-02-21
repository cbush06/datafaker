from enum import Enum, auto
from typing import Callable


class SourceType(Enum):
    SQL = auto()
    DOC = auto()

class ManyToMany:
    _doc_name: str = None
    _metadata: dict[str, any] = None

    _validators: dict[str, Callable[[any], bool]] = {
        'limit': lambda _, val: val == None or (isinstance(val, int) and val > 0),
        'left_doc': lambda _, val: val == None or (isinstance(val, str) and len(val.strip()) > 0),
        'right_doc': lambda _, val: val == None or (isinstance(val, str) and len(val.strip()) > 0),
        'left_sql': lambda _, val: val == None or (isinstance(val, str) and len(val.strip()) > 0),
        'right_sql': lambda _, val: val == None or (isinstance(val, str) and len(val.strip()) > 0),
        'left_filter': lambda _, val: val == None or (isinstance(val, str) and len(val.strip()) > 0),
        'right_filter': lambda _, val: val == None or (isinstance(val, str) and len(val.strip()) > 0)
    }

    def __init__(self, doc_name: str, many_to_many: dict[str, any]):
        self._doc_name = doc_name
        self._metadata = {
            'limit': None,
            'left_doc': None,
            'right_doc': None,
            'left_sql': None,
            'right_sql': None,
            'left_filter': None,
            'right_filter': None
        }

        for key in many_to_many:
            self._extract_metadata_entry(key, many_to_many[key])

        self._validate_all()

    def _extract_metadata_entry(self, key: str, entry):
        if(key in self._metadata):
            if(self._validators[key](self, entry)):
                self._metadata[key] = entry
            else:
                raise ValueError(f"Value for {self._doc_name}._many_to_many.{key} is invalid")
        else:
            raise ValueError(f"Metadata entry {self._doc_name}._many_to_many.{key} is not recognized")
    
    def _validate_all(self):
        # Must have left and right source
        has_left = self.get_left_doc()!= None or self.get_left_sql() != None
        has_right = self.get_right_doc() != None or self.get_right_sql() != None
        if(not(has_left and has_right)):
            raise ValueError(f"Value for {self._docname}._many_to_many must have both a left and right source")

    def get_metadata_entry(self, key):
        return self._metadata[key]
    
    def get_left_type(self):
        return SourceType.DOC if self.get_left_doc() != None else SourceType.SQL
    
    def get_right_type(self):
        return SourceType.DOC if self.get_right_doc != None else SourceType.SQL
    
    def get_left_doc(self):
        return self._metadata['left_doc']
    
    def get_right_doc(self):
        return self._metadata['right_doc']
    
    def get_left_sql(self):
        return self._metadata['left_sql']
    
    def get_right_sql(self):
        return self._metadata['right_sql']
    
    def get_limit(self):
        return self._metadata['limit']
    
    def filter_left(self, context):
        return self._metadata['left_filter'] == None or eval(self._metadata['left_filter'], context)
    
    def filter_right(self, context):
        return self._metadata['right_filter'] == None or eval(self._metadata['right_filter'], context)