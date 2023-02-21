from enum import Enum, auto
from typing import Callable
from structs.from_doc import FromDoc
from structs.from_sql import FromSql

from structs.many_to_many import ManyToMany

class CardinalityIndicator(Enum):
    SQL = auto()
    DOC = auto()
    COUNT = auto()
    MANY = auto()
    EMPTY = auto()

class DocumentMetadata:
    _doc_name: str = None
    _doc: dict[str, any] = None
    _cardinality_indicator: CardinalityIndicator = None
    _metadata: dict[str, any] = None

    _validators: dict[str, Callable[[any], bool]] = {
        'count': lambda _, val: isinstance(val, int) and val > 0,
        'from_doc': lambda _, val: True,
        'from_sql': lambda _, val: True,
        'empty': lambda _, val: True,
        'many_to_many': lambda _, val: True # Validation is done by ManyToMany class
    }

    def __init__(self, doc_name: str, doc: dict[str, any]):
        self._doc_name = doc_name
        self._doc = doc
        self._cardinality_indicator = CardinalityIndicator.COUNT
        self._metadata = {
            'count': 1,
            'from_doc': None,
            'from_sql': None,
            'empty': None,
            'many_to_many': None
        }

        for key in doc:
            if(key[:1] == '_'):
                self._extract_metadata_entry(key[1:], doc[key])
        
        self._validate_all()

    def _extract_metadata_entry(self, key: str, entry):
        if(key in self._metadata):
            if(self._validators[key](self, entry)):
                if(key == 'empty'):
                    # _empty is a flag used to include docs with no contents (e.g., if you need to truncate a table without loading it)
                    self._metadata[key] = True
                elif(key == 'many_to_many'):
                    self._metadata[key] = ManyToMany(self._doc_name, entry)
                elif(key == 'from_doc'):
                    self._metadata[key] = FromDoc(self._doc_name, entry)
                elif(key == 'from_sql'):
                    self._metadata[key] = FromSql(self._doc_name, entry)
                else:
                    self._metadata[key] = entry
            else:
                raise ValueError(f"Value for {self._doc_name}._{key} is invalid")
        else:
            raise ValueError(f"Metadata entry _{key} is not recognized")

    
    def _validate_all(self):
        # Only one of (from_doc, from_sql, count, many) may be used
        cardinality_indicators = 0
        if(self.get_metadata_entry('count') > 1): 
            cardinality_indicators += 1
            self._cardinality_indicator = CardinalityIndicator.COUNT
        if(self.get_metadata_entry('from_doc') != None): 
            cardinality_indicators += 1
            self._cardinality_indicator = CardinalityIndicator.DOC
        if(self.get_metadata_entry('from_sql') != None): 
            cardinality_indicators += 1
            self._cardinality_indicator = CardinalityIndicator.SQL
        if(self.get_metadata_entry('many_to_many') != None):
            cardinality_indicators += 1
            self._cardinality_indicator = CardinalityIndicator.MANY
        if(self.get_metadata_entry('empty') == True):
            cardinality_indicators += 1
            self._cardinality_indicator = CardinalityIndicator.EMPTY
        if(cardinality_indicators > 1):
            raise ValueError("Only one of (from_doc, from_sql, count, empty) may be used")
    
    def get_metadata_entry(self, key):
        return self._metadata[key]
    
    def get_cardinality_indicator(self):
        return self._cardinality_indicator
