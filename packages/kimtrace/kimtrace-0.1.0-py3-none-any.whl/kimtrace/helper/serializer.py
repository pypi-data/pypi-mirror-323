import orjson
from typing import Any, List

def serialize_with_redactor(redactors: List[str] = [], obj: Any = None) -> str:
    def redactor_handler(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                key: '[REDACTED]' if any(field.lower() == key.lower() for field in redactors) 
                else redactor_handler(value)
                for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [redactor_handler(item) for item in obj]
        return obj
    
    redacted_obj = redactor_handler(obj)
    return orjson.dumps(redacted_obj).decode('utf-8')