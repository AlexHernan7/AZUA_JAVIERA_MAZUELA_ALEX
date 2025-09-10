"""
API routes para VecindApp.
"""

from .routes.auth_routes import router as auth_router
from .routes.user_routes import router as user_router

__all__ = [
    "auth_router",
    "user_router"
]
