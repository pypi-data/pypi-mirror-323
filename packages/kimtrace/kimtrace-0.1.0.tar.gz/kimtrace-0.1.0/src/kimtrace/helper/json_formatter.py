import orjson
import traceback

def jsonify_error(error: Exception) -> str:
    error_dict = {
        "name": error.__class__.__name__,
        "message": str(error),
        "stack": ''.join(traceback.format_tb(error.__traceback__)) if error.__traceback__ else None,
    }
    
    return orjson.dumps(error_dict).decode('utf-8')