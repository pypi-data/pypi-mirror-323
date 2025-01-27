from typing import Any, List, Set

def get_tag_values(tags: List[str] = [], obj: Any = None) -> List[str]:
    result: Set[str] = set()
    
    def search_object(current_obj: Any, current_tags: List[str]) -> None:
        if not isinstance(current_obj, dict):
            return
            
        for key, value in current_obj.items():
            if any(field.lower() == key.lower() for field in current_tags):
                if not isinstance(value, (dict, list, set)):
                    result.add(str(value))
            
            if isinstance(value, dict):
                search_object(value, current_tags)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        search_object(item, current_tags)
    
    search_object(obj, tags)
    
    return list(result)