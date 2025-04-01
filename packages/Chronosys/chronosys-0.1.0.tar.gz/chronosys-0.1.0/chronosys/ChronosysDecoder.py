import json
import uuid
from datetime import datetime
from typing import Dict, Any


class ChronosysDecoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct: Dict[str, Any]) -> Any:
        if "__datetime__" in dct:
            return datetime.fromisoformat(dct["value"])
        if "__uuid__" in dct:
            return uuid.UUID(dct["value"])
        if "__class__" in dct:
            return type(dct["__class__"], (), dct["value"])
        return dct
