from typing import Any

from faker import Faker


class RecordContext:

    def get_resovled(self) -> dict[str, Any]:
        pass

    def field(self, name) -> Any:
        pass
    
    def from_field(self, name) -> Any:
        pass
    
    def fake(self) -> Faker:
        pass

    def get_multiply_idx(self) -> int:
        pass