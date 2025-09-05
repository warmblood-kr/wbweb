"""
Authentication and authorization framework for wbweb.

Provides Django-like permission system with pluggable policies.
"""

from .permissions import PermissionMixin
from .policies import PermissionRegistry, register_permission, get_permission_registry

__all__ = [
    'PermissionMixin',
    'PermissionRegistry', 
    'register_permission',
    'get_permission_registry',
]