"""Main entrypoint into package.

This is the ONLY public interface into the package. All other modules are
to be considered private and subject to change without notice.
"""

from aibaba_ai_api.api_handler import APIHandler
from aibaba_ai_api.client import RemoteRunnable
from aibaba_ai_api.schema import CustomUserType
from aibaba_ai_api.server import add_routes
from aibaba_ai_api.version import __version__

__all__ = [
    "RemoteRunnable",
    "APIHandler",
    "add_routes",
    "__version__",
    "CustomUserType",
]
