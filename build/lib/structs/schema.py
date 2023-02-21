from typing import Union
import yaml

from structs.global_metadata import GlobalMetadata

class Schema:
    _schema: dict[str, Union[dict[str, any], list[dict[str, any]]]] = None
    _metadata: GlobalMetadata = None

    def __init__(self, path):
        with open(path, 'r') as file:
            self._schema = yaml.safe_load(file)
        self._metadata = GlobalMetadata(self._schema)
    
    def list_documents(self):
        return list(filter(lambda k: k[:1] != '_', self._schema.keys()))
    
    def get_document(self, name):
        return self._schema[name]
    
    def get_document_type(self, name):
        return type(self.get_document(name))
    
    def get_metadata_entry(self, key):
        return self._metadata.get_metadata_entry(key)
    
    def get_metadata(self):
        return self._metadata