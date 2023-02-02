"""
    Utils for ORM management.
"""

from typing import Dict, Any


def edit_orm_instance_fields(
    instance: Any, fields_map: Dict[str, Any], allow_undefined: bool = False
) -> bool:
    orm_instance_is_changed = False
    for attr_name, attr_value in fields_map.items():
        if not allow_undefined and not attr_value:
            continue
        if attr_value != getattr(instance, attr_name, None):
            setattr(instance, attr_name, attr_value)
            orm_instance_is_changed = True
    return orm_instance_is_changed
