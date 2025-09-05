"""
Permission policy registry for wbweb.

Unified permission system supporting both global and object-specific permissions.
"""

from typing import Dict, Callable, Tuple, Type, List


class PermissionRegistry:
    """Registry for permission checker functions"""
    
    def __init__(self):
        # Single storage: (resource_type, action) -> checker_func
        # Global permissions use (None, perm_name) as key
        self._permissions: Dict[Tuple[Type | None, str], Callable] = {}
    
    def register(self, perm_name: str, resource_type: Type = None, checker_func: Callable = None):
        """Register permission checker function"""
        key = (resource_type, perm_name)
        self._permissions[key] = checker_func
    
    async def check(self, user, perm_or_action: str, obj=None) -> bool | None:
        """Check permission using registered checker functions"""
        resource_type = type(obj) if obj is not None else None
        key = (resource_type, perm_or_action)
        
        if key in self._permissions:
            checker_func = self._permissions[key]
            if obj is None:
                # Global permission - only pass user
                return await checker_func(user)
            else:
                # Object permission - pass user and object
                return await checker_func(user, obj)
        return None  # No opinion on unregistered permission


# Global registry instance
_permission_registry = PermissionRegistry()


def register_permission(perm_name: str, resource_type: Type = None):
    """
    Decorator to register permission checker functions
    
    Args:
        perm_name: Permission name (for global) or action name (for object)
        resource_type: Resource type for object permissions, None for global
    """
    def decorator(func: Callable):
        _permission_registry.register(perm_name, resource_type, func)
        return func
    return decorator


def get_permission_registry() -> PermissionRegistry:
    """Get the global permission registry"""
    return _permission_registry