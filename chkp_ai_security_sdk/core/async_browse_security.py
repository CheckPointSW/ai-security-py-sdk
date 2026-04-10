import asyncio
from chkp_ai_security_sdk.classes.infinity_portal_auth import InfinityPortalAuth
from chkp_ai_security_sdk.classes.sdk_connection_state import SDKConnectionState
from chkp_ai_security_sdk.core.session_manager import SessionManager
from chkp_ai_security_sdk.generated_browse_async.api import _ApiMixin


class AsyncBrowseSecurity(_ApiMixin):
    """Check Point Browse Security SDK (async) - manage Browse Security policies and assets."""

    def __init__(self):
        self._session_manager = SessionManager()
        self._api_client = None

    async def connect(self, infinity_portal_auth: InfinityPortalAuth):
        """Connect to Browse Security service using CloudInfra API credentials."""
        await asyncio.to_thread(self._session_manager.connect, infinity_portal_auth)

    async def disconnect(self):
        """Disconnect and stop all background session management."""
        if self._api_client is not None:
            await self._api_client.close()
            self._api_client = None
        await asyncio.to_thread(self._session_manager.disconnect)

    def connection_state(self) -> SDKConnectionState:
        """Returns the current connection state."""
        return self._session_manager.connection_state()

    @staticmethod
    def info() -> str:
        """Returns SDK build and spec information."""
        try:
            from chkp_ai_security_sdk.generated_browse_async.sdk_build import sdk_build_info
            return str(sdk_build_info())
        except Exception:
            return 'SDK info not available (run sdk_generator/generate_sdk.py first)'

    def _get_api_client(self):
        sync_cfg = self._session_manager.client_configuration
        if self._api_client is None:
            from chkp_ai_security_sdk.generated_browse_async.api_client import ApiClient
            from chkp_ai_security_sdk.generated_browse_async.configuration import Configuration
            cfg = Configuration()
            cfg.host = sync_cfg.host
            cfg.access_token = sync_cfg.access_token
            cfg.client_id = getattr(sync_cfg, 'client_id', None)
            self._api_client = ApiClient(cfg)
        else:
            self._api_client.configuration.access_token = sync_cfg.access_token
        return self._api_client
