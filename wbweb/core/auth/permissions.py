"""
Permission mixin for user models.

Provides has_perm() method for checking permissions anywhere in the application.
"""

from .policies import get_permission_registry


class PermissionMixin:
    """Mixin to add permission checking methods to User models"""
    
    async def has_perm(self, perm: str, obj=None) -> bool:
        """
        Check if user has permission
        
        Args:
            perm: Permission name (global) or action name (object-specific)
            obj: Resource object for object permissions, None for global
            
        Returns:
            bool: True if permission granted, False if denied or no opinion
        """
        registry = get_permission_registry()
        result = await registry.check(self, perm, obj)
        
        # None means no opinion -> default deny (secure by default)
        # False means explicit deny
        # True means explicit allow
        return result is True