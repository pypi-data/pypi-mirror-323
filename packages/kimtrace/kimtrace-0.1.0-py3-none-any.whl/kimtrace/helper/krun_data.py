from typing import Any, Optional
from ..storage.context_vars import storage, KRunStorageData
from typing_extensions import TypeGuard

def get_krun_data() -> Optional[KRunStorageData]: 
    try:
        return storage.get()
    except Exception:
        return None

def is_krun_data(x: Any) -> TypeGuard[KRunStorageData]:
    if x is None:
        return False
        
    if isinstance(x, dict):
        return ('context' in x and 
                isinstance(x['context'], dict) and
                'runName' in x['context'] and 
                'id' in x['context'])
    
    if isinstance(x, KRunStorageData):
        return (hasattr(x, 'context') and 
                hasattr(x.context, 'runName') and 
                hasattr(x.context, 'id'))
    
    return False