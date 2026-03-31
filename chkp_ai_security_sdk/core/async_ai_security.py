import asyncio
from typing import Any
from chkp_ai_security_sdk.classes.infinity_portal_auth import InfinityPortalAuth
from chkp_ai_security_sdk.classes.sdk_connection_state import SDKConnectionState
from chkp_ai_security_sdk.core.ai_security import AISecurity


class _AsyncApiProxy:
    """Wraps a synchronous API instance, making all public methods awaitable."""

    def __init__(self, sync_api: Any):
        self._sync = sync_api

    def __getattr__(self, name: str):
        attr = getattr(self._sync, name)
        if callable(attr):
            async def _async_wrapper(*args, **kwargs):
                return await asyncio.to_thread(attr, *args, **kwargs)
            return _async_wrapper
        return attr


class AsyncAISecurity:
    """Check Point AI Security SDK (async) - manage AI Security policies and assets."""

    def __init__(self):
        self._sync = AISecurity()

    async def connect(self, infinity_portal_auth: InfinityPortalAuth):
        await asyncio.to_thread(self._sync.connect, infinity_portal_auth)

    async def disconnect(self):
        await asyncio.to_thread(self._sync.disconnect)

    def connection_state(self) -> SDKConnectionState:
        return self._sync.connection_state()

    @staticmethod
    def info() -> str:
        return AISecurity.info()

    def __getattr__(self, name: str):
        """Dynamically proxy any API property from the sync SDK through _AsyncApiProxy."""
        # Delegate to the sync instance — if it's an API object, wrap it
        attr = getattr(self._sync, name)
        return _AsyncApiProxy(attr)
