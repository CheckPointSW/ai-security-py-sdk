import json
import threading
import uuid
import requests
from typing import Any
from urllib.parse import urlparse

from chkp_ai_security_sdk.classes.workforceai_api_exception import WorkforceAIApiException, WorkforceAIErrorScope
from chkp_ai_security_sdk.classes.infinity_portal_auth import InfinityPortalAuth
from chkp_ai_security_sdk.classes.sdk_connection_state import SDKConnectionState
from chkp_ai_security_sdk.core.logger import logger, error_logger
from chkp_ai_security_sdk.core.sdk_platform import KEEP_ALIVE_GRACE_SECONDS

CI_AUTH_PATH = '/auth/external'
SOURCE_HEADER = 'ai-security-py-sdk'


class SessionManager:
    def __init__(self):
        self.__infinity_portal_auth: InfinityPortalAuth = None
        self.__jwt_token: str = ''
        self.__session_id: str = str(uuid.uuid4())
        self.__url: str = ''
        self.__keep_alive_on_flag: bool = False
        self.__keep_alive_event: threading.Event = threading.Event()
        self.__sdk_connection_state: SDKConnectionState = SDKConnectionState.DISCONNECTED
        self.__token_expires_in: int = 0

    @property
    def client_configuration(self) -> Any:
        self.__check_connected()
        from chkp_ai_security_sdk.generated.configuration import Configuration
        configuration = Configuration()
        configuration.host = self.__url
        configuration.access_token = self.__jwt_token
        configuration.client_id = self.__infinity_portal_auth.client_id if self.__infinity_portal_auth else None
        return configuration

    def __perform_ci_login(self):
        auth_url = f'{self.__url}{CI_AUTH_PATH}'
        try:
            logger(f'Performing CI login for session "{self.__session_id}" with url "{auth_url}"...')
            payload = {
                'clientId': self.__infinity_portal_auth.client_id,
                'accessKey': self.__infinity_portal_auth.access_key,
            }
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url=auth_url, data=json.dumps(payload), headers=headers)

            if not 200 <= response.status_code <= 299:
                error_logger(f'CI login failed with status "{response.status_code}" for session "{self.__session_id}"')
                raise WorkforceAIApiException(
                    error_scope=WorkforceAIErrorScope.SERVICE,
                    payload_error=response.text,
                    url=auth_url,
                    status_code=response.status_code,
                )

            response_json = response.json()
            if not response_json.get('success'):
                error_logger(f'CI login failed for session "{self.__session_id}"')
                raise WorkforceAIApiException(error_scope=WorkforceAIErrorScope.SERVICE, payload_error=str(response_json))

            self.__jwt_token = response_json['data']['token']
            self.__token_expires_in = response_json['data'].get('expiresIn', 1800)
            self.__sdk_connection_state = SDKConnectionState.CONNECTED
            logger(f'CI login succeeded for session "{self.__session_id}", token expires in {self.__token_expires_in}s')

        except WorkforceAIApiException:
            self.__sdk_connection_state = SDKConnectionState.CONNECTION_ISSUE
            raise
        except Exception as e:
            error_logger(f'CI login failed for session "{self.__session_id}": {e}')
            self.__sdk_connection_state = SDKConnectionState.CONNECTION_ISSUE
            raise WorkforceAIApiException(error_scope=WorkforceAIErrorScope.NETWORKING, network_error=e)

    def __refresh_delay(self) -> float:
        """Calculate seconds to sleep before next token refresh."""
        delay = self.__token_expires_in - KEEP_ALIVE_GRACE_SECONDS
        return max(delay, 1)

    def __keep_alive_loop(self):
        while self.__keep_alive_on_flag:
            delay = self.__refresh_delay()
            logger(f'Next token refresh for session {self.__session_id} in {delay}s')
            # Wait for delay or until signaled to stop
            self.__keep_alive_event.wait(timeout=delay)
            if not self.__keep_alive_on_flag:
                break
            self.__keep_alive_event.clear()
            try:
                logger(f'Refreshing CI token for session {self.__session_id}...')
                self.__perform_ci_login()
                logger(f'CI token refreshed for session {self.__session_id}')
            except Exception as e:
                error_logger(f'Token refresh failed for session {self.__session_id}: {e}')
                self.__sdk_connection_state = SDKConnectionState.CONNECTION_ISSUE

    def __activate_keep_alive(self):
        logger(f'Starting keep-alive for session {self.__session_id}')
        self.__keep_alive_on_flag = True
        self.__keep_alive_event.clear()
        thread = threading.Thread(target=self.__keep_alive_loop)
        thread.daemon = True
        thread.start()

    def __validate_params(self, infinity_portal_auth: InfinityPortalAuth):
        if not infinity_portal_auth.gateway:
            raise WorkforceAIApiException(error_scope=WorkforceAIErrorScope.INVALID_PARAMS, message='gateway is mandatory')
        if not infinity_portal_auth.client_id:
            raise WorkforceAIApiException(error_scope=WorkforceAIErrorScope.INVALID_PARAMS, message='client_id is mandatory')
        if not infinity_portal_auth.access_key:
            raise WorkforceAIApiException(error_scope=WorkforceAIErrorScope.INVALID_PARAMS, message='access_key is mandatory')
        try:
            parsed = urlparse(infinity_portal_auth.gateway)
            if parsed.scheme != 'https':
                raise WorkforceAIApiException(
                    error_scope=WorkforceAIErrorScope.INVALID_PARAMS,
                    message=f'Gateway must use https, got: {infinity_portal_auth.gateway}',
                )
            infinity_portal_auth.gateway = f'{parsed.scheme}://{parsed.netloc}'
        except WorkforceAIApiException:
            raise
        except Exception as e:
            raise WorkforceAIApiException(error_scope=WorkforceAIErrorScope.INVALID_PARAMS, message=f'Invalid gateway URL: {e}')

    def connect(self, infinity_portal_auth: InfinityPortalAuth):
        self.__sdk_connection_state = SDKConnectionState.CONNECTING
        self.__validate_params(infinity_portal_auth)
        self.__infinity_portal_auth = infinity_portal_auth
        self.__url = infinity_portal_auth.gateway
        logger(f'New session {self.__session_id} connecting to {self.__url}')
        self.__perform_ci_login()
        self.__activate_keep_alive()

    def disconnect(self):
        logger(f'Disconnecting session {self.__session_id}')
        self.__sdk_connection_state = SDKConnectionState.DISCONNECTED
        self.__keep_alive_on_flag = False
        self.__keep_alive_event.set()  # Wake up sleeping thread so it exits
        self.__jwt_token = ''
        self.__session_id = str(uuid.uuid4())

    def connection_state(self) -> SDKConnectionState:
        return self.__sdk_connection_state

    def __check_connected(self):
        if self.__sdk_connection_state == SDKConnectionState.DISCONNECTED:
            error_logger('Unable to process operation call, no session configured, connect first')
            raise WorkforceAIApiException(error_scope=WorkforceAIErrorScope.SESSION, message='No session configured, connect first')
