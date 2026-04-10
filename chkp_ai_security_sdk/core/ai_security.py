from chkp_ai_security_sdk.classes.infinity_portal_auth import InfinityPortalAuth
from chkp_ai_security_sdk.classes.sdk_connection_state import SDKConnectionState
from chkp_ai_security_sdk.core.session_manager import SessionManager
from chkp_ai_security_sdk.generated.api import _ApiMixin

print_message = True


class AISecurity(_ApiMixin):
    """Check Point AI Security SDK - manage AI Security policies and assets."""

    def __init__(self):
        self._session_manager = SessionManager()
        if print_message:
            print('Check Point AI Security SDK - https://github.com/CheckPointSW/ai-security-py-sdk')

    def connect(self, infinity_portal_auth: InfinityPortalAuth):
        """Connect to AI Security service using CloudInfra API credentials."""
        self._session_manager.connect(infinity_portal_auth)

    def disconnect(self):
        """Disconnect and stop all background session management."""
        self._session_manager.disconnect()

    def connection_state(self) -> SDKConnectionState:
        """Returns the current connection state."""
        return self._session_manager.connection_state()

    @staticmethod
    def info() -> str:
        """Returns SDK build and spec information."""
        try:
            from chkp_ai_security_sdk.generated.sdk_build import sdk_build_info
            return str(sdk_build_info())
        except Exception:
            return 'SDK info not available (run sdk_generator/generate_sdk.py first)'

    def _get_api_client(self):
        from chkp_ai_security_sdk.generated.api_client import ApiClient
        return ApiClient(self._session_manager.client_configuration)
