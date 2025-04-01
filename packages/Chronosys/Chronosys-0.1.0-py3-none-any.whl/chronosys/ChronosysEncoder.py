import json
import uuid
from datetime import datetime
from typing import Any


class ChronosysEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return {"__datetime__": True, "value": obj.isoformat()}
        if isinstance(obj, uuid.UUID):
            return {"__uuid__": True, "value": str(obj)}
        if hasattr(obj, "__dict__"):
            return {"__class__": obj.__class__.__name__, "value": obj.__dict__}
        return super().default(obj)
