"""
Optional session context management for wbweb.

This provides Django-style session sharing while maintaining full backward compatibility.
Existing code continues to work unchanged, but new features can opt into session sharing.

Uses Python's native contextvars for proper async support with no external dependencies.
"""

import contextvars
from typing import Optional
from contextlib import contextmanager
from sqlalchemy.ext.asyncio import AsyncSession

# Use Python's native ContextVar - designed for async/await contexts
_session_context: contextvars.ContextVar[Optional[AsyncSession]] = contextvars.ContextVar(
    'session_context', default=None
)


class SessionContext:
    """
    Optional session context for sharing sessions across Manager operations.
    
    This is completely optional - if not used, wbweb behaves exactly as before.
    When used, it enables Django-style session sharing.
    
    Uses Python's native contextvars for proper async support with automatic cleanup.
    """
    
    def get_current_session(self) -> Optional[AsyncSession]:
        """Get the current session for this context, if any."""
        return _session_context.get()
    
    def set_current_session(self, session: AsyncSession) -> None:
        """Set the current session for this context."""
        _session_context.set(session)
    
    def clear_current_session(self) -> None:
        """Clear the current session for this context."""
        _session_context.set(None)
    
    @contextmanager
    def session_context(self, session: AsyncSession):
        """
        Context manager to set a session as current for all Manager operations.
        
        Usage:
            session = await get_session()
            async with session:
                with session_context.session_context(session):
                    # All Manager operations will use this session
                    user = await User.objects.create(email='test@example.com')
                    org = await Organization.objects.create(name='MyOrg')
                    # Both user and org are in the same session!
        """
        old_session = self.get_current_session()
        try:
            self.set_current_session(session)
            yield
        finally:
            if old_session is not None:
                self.set_current_session(old_session)
            else:
                self.clear_current_session()


# Global session context instance - optional to use
session_context = SessionContext()


def get_context_session() -> Optional[AsyncSession]:
    """
    Get the current context session if one is set.
    
    This is used internally by the enhanced get_session() function.
    Returns None if no context session is active.
    """
    return session_context.get_current_session()