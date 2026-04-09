"""Unit tests for SDK classes — no credentials required.

Tests cover:
- SDK instantiation (sync + async, both products)
- Connection state lifecycle
- InfinityPortalAuth validation
- SessionManager error handling
- Info / build info
- Disconnect idempotency
- API property access before connect raises
"""
import asyncio
import unittest
from unittest.mock import patch, MagicMock

from chkp_ai_security_sdk import (
    AISecurity,
    AsyncAISecurity,
    BrowseSecurity,
    AsyncBrowseSecurity,
    InfinityPortalAuth,
    SDKConnectionState,
    WorkforceAIApiException,
    WorkforceAIErrorScope,
)


def _mock_successful_login(session_manager):
    """Patch perform_ci_login to set CONNECTED state without real HTTP."""

    def fake_login():
        session_manager._SessionManager__sdk_connection_state = SDKConnectionState.CONNECTED
        session_manager._SessionManager__jwt_token = 'fake-jwt-token'

    return patch.object(
        session_manager, '_SessionManager__perform_ci_login', side_effect=fake_login
    )


# ────────────────────────────────────────────
# InfinityPortalAuth
# ────────────────────────────────────────────

class TestInfinityPortalAuth(unittest.TestCase):

    def test_stores_credentials(self):
        auth = InfinityPortalAuth(client_id='cid', access_key='key', gateway='https://gw.example.com')
        self.assertEqual(auth.client_id, 'cid')
        self.assertEqual(auth.access_key, 'key')
        self.assertEqual(auth.gateway, 'https://gw.example.com')


# ────────────────────────────────────────────
# SessionManager validation
# ────────────────────────────────────────────

class TestSessionManagerValidation(unittest.TestCase):

    def _make_auth(self, **overrides):
        defaults = dict(client_id='cid', access_key='key', gateway='https://gw.example.com')
        defaults.update(overrides)
        return InfinityPortalAuth(**defaults)

    def test_missing_gateway(self):
        from chkp_ai_security_sdk.core.session_manager import SessionManager
        sm = SessionManager()
        with self.assertRaises(WorkforceAIApiException) as ctx:
            sm.connect(self._make_auth(gateway=''))
        self.assertEqual(ctx.exception.error_scope, WorkforceAIErrorScope.INVALID_PARAMS)

    def test_missing_client_id(self):
        from chkp_ai_security_sdk.core.session_manager import SessionManager
        sm = SessionManager()
        with self.assertRaises(WorkforceAIApiException) as ctx:
            sm.connect(self._make_auth(client_id=''))
        self.assertEqual(ctx.exception.error_scope, WorkforceAIErrorScope.INVALID_PARAMS)

    def test_missing_access_key(self):
        from chkp_ai_security_sdk.core.session_manager import SessionManager
        sm = SessionManager()
        with self.assertRaises(WorkforceAIApiException) as ctx:
            sm.connect(self._make_auth(access_key=''))
        self.assertEqual(ctx.exception.error_scope, WorkforceAIErrorScope.INVALID_PARAMS)

    def test_non_https_gateway(self):
        from chkp_ai_security_sdk.core.session_manager import SessionManager
        sm = SessionManager()
        with self.assertRaises(WorkforceAIApiException) as ctx:
            sm.connect(self._make_auth(gateway='http://gw.example.com'))
        self.assertEqual(ctx.exception.error_scope, WorkforceAIErrorScope.INVALID_PARAMS)

    def test_gateway_strips_path(self):
        from chkp_ai_security_sdk.core.session_manager import SessionManager
        auth = self._make_auth(gateway='https://gw.example.com/some/path')
        sm = SessionManager()
        # validate_params mutates auth.gateway, but connect will fail on CI login
        # We just verify validation passes for the gateway format
        with patch.object(sm, '_SessionManager__perform_ci_login'):
            with patch.object(sm, '_SessionManager__activate_keep_alive'):
                sm.connect(auth)
        self.assertEqual(auth.gateway, 'https://gw.example.com')


# ────────────────────────────────────────────
# Sync SDK classes — AISecurity
# ────────────────────────────────────────────

class TestAISecurity(unittest.TestCase):

    def test_initial_state_disconnected(self):
        ai = AISecurity()
        self.assertEqual(ai.connection_state(), SDKConnectionState.DISCONNECTED)

    def test_info_returns_string(self):
        info = AISecurity.info()
        self.assertIsInstance(info, str)
        self.assertTrue(len(info) > 0)

    def test_api_property_before_connect_raises(self):
        ai = AISecurity()
        with self.assertRaises(WorkforceAIApiException) as ctx:
            _ = ai.chats_policy_api
        self.assertEqual(ctx.exception.error_scope, WorkforceAIErrorScope.SESSION)

    def test_connect_and_disconnect(self):
        ai = AISecurity()
        auth = InfinityPortalAuth(client_id='cid', access_key='key', gateway='https://gw.example.com')
        with _mock_successful_login(ai._session_manager):
            with patch.object(ai._session_manager, '_SessionManager__activate_keep_alive'):
                ai.connect(auth)
        self.assertEqual(ai.connection_state(), SDKConnectionState.CONNECTED)
        ai.disconnect()
        self.assertEqual(ai.connection_state(), SDKConnectionState.DISCONNECTED)

    def test_disconnect_idempotent(self):
        ai = AISecurity()
        ai.disconnect()
        ai.disconnect()
        self.assertEqual(ai.connection_state(), SDKConnectionState.DISCONNECTED)

    def test_has_all_api_properties(self):
        expected = [
            'agents_policy_api', 'ai_access_policy_api', 'apps_catalog_api',
            'chats_policy_api', 'deployment_status_api', 'dlp_datatypes_api',
            'rulebase_api', 'users_api',
        ]
        for prop in expected:
            self.assertTrue(hasattr(AISecurity, prop), f'Missing property: {prop}')


# ────────────────────────────────────────────
# Sync SDK classes — BrowseSecurity
# ────────────────────────────────────────────

class TestBrowseSecurity(unittest.TestCase):

    def test_initial_state_disconnected(self):
        browse = BrowseSecurity()
        self.assertEqual(browse.connection_state(), SDKConnectionState.DISCONNECTED)

    def test_info_returns_string(self):
        info = BrowseSecurity.info()
        self.assertIsInstance(info, str)
        self.assertTrue(len(info) > 0)

    def test_api_property_before_connect_raises(self):
        browse = BrowseSecurity()
        with self.assertRaises(WorkforceAIApiException) as ctx:
            _ = browse.dlp_policy_api
        self.assertEqual(ctx.exception.error_scope, WorkforceAIErrorScope.SESSION)

    def test_connect_and_disconnect(self):
        browse = BrowseSecurity()
        auth = InfinityPortalAuth(client_id='cid', access_key='key', gateway='https://gw.example.com')
        with _mock_successful_login(browse._session_manager):
            with patch.object(browse._session_manager, '_SessionManager__activate_keep_alive'):
                browse.connect(auth)
        self.assertEqual(browse.connection_state(), SDKConnectionState.CONNECTED)
        browse.disconnect()
        self.assertEqual(browse.connection_state(), SDKConnectionState.DISCONNECTED)

    def test_has_all_api_properties(self):
        expected = [
            'apps_catalog_api', 'deployment_status_api', 'dlp_datatypes_api',
            'dlp_policy_api', 'objects_api', 'rulebase_api',
            'secure_browsing_policy_api', 'users_api', 'web_access_policy_api',
        ]
        for prop in expected:
            self.assertTrue(hasattr(BrowseSecurity, prop), f'Missing property: {prop}')


# ────────────────────────────────────────────
# Async SDK classes — AsyncAISecurity
# ────────────────────────────────────────────

class TestAsyncAISecurity(unittest.TestCase):

    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_initial_state_disconnected(self):
        ai = AsyncAISecurity()
        self.assertEqual(ai.connection_state(), SDKConnectionState.DISCONNECTED)

    def test_info_returns_string(self):
        info = AsyncAISecurity.info()
        self.assertIsInstance(info, str)
        self.assertTrue(len(info) > 0)

    def test_api_property_before_connect_raises(self):
        ai = AsyncAISecurity()
        with self.assertRaises(WorkforceAIApiException) as ctx:
            _ = ai.chats_policy_api
        self.assertEqual(ctx.exception.error_scope, WorkforceAIErrorScope.SESSION)

    def test_connect_and_disconnect(self):
        ai = AsyncAISecurity()
        auth = InfinityPortalAuth(client_id='cid', access_key='key', gateway='https://gw.example.com')

        async def _test():
            with _mock_successful_login(ai._session_manager):
                with patch.object(ai._session_manager, '_SessionManager__activate_keep_alive'):
                    await ai.connect(auth)
            self.assertEqual(ai.connection_state(), SDKConnectionState.CONNECTED)
            await ai.disconnect()
            self.assertEqual(ai.connection_state(), SDKConnectionState.DISCONNECTED)

        self._run(_test())

    def test_disconnect_idempotent(self):
        ai = AsyncAISecurity()

        async def _test():
            await ai.disconnect()
            await ai.disconnect()
            self.assertEqual(ai.connection_state(), SDKConnectionState.DISCONNECTED)

        self._run(_test())

    def test_has_all_api_properties(self):
        expected = [
            'agents_policy_api', 'ai_access_policy_api', 'apps_catalog_api',
            'chats_policy_api', 'deployment_status_api', 'dlp_datatypes_api',
            'rulebase_api', 'users_api',
        ]
        for prop in expected:
            self.assertTrue(hasattr(AsyncAISecurity, prop), f'Missing property: {prop}')


# ────────────────────────────────────────────
# Async SDK classes — AsyncBrowseSecurity
# ────────────────────────────────────────────

class TestAsyncBrowseSecurity(unittest.TestCase):

    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_initial_state_disconnected(self):
        browse = AsyncBrowseSecurity()
        self.assertEqual(browse.connection_state(), SDKConnectionState.DISCONNECTED)

    def test_info_returns_string(self):
        info = AsyncBrowseSecurity.info()
        self.assertIsInstance(info, str)
        self.assertTrue(len(info) > 0)

    def test_api_property_before_connect_raises(self):
        browse = AsyncBrowseSecurity()
        with self.assertRaises(WorkforceAIApiException) as ctx:
            _ = browse.dlp_policy_api
        self.assertEqual(ctx.exception.error_scope, WorkforceAIErrorScope.SESSION)

    def test_connect_and_disconnect(self):
        browse = AsyncBrowseSecurity()
        auth = InfinityPortalAuth(client_id='cid', access_key='key', gateway='https://gw.example.com')

        async def _test():
            with _mock_successful_login(browse._session_manager):
                with patch.object(browse._session_manager, '_SessionManager__activate_keep_alive'):
                    await browse.connect(auth)
            self.assertEqual(browse.connection_state(), SDKConnectionState.CONNECTED)
            await browse.disconnect()
            self.assertEqual(browse.connection_state(), SDKConnectionState.DISCONNECTED)

        self._run(_test())

    def test_has_all_api_properties(self):
        expected = [
            'apps_catalog_api', 'deployment_status_api', 'dlp_datatypes_api',
            'dlp_policy_api', 'objects_api', 'rulebase_api',
            'secure_browsing_policy_api', 'users_api', 'web_access_policy_api',
        ]
        for prop in expected:
            self.assertTrue(hasattr(AsyncBrowseSecurity, prop), f'Missing property: {prop}')


# ────────────────────────────────────────────
# WorkforceAIApiException
# ────────────────────────────────────────────

class TestWorkforceAIApiException(unittest.TestCase):

    def test_exception_fields(self):
        exc = WorkforceAIApiException(
            error_scope=WorkforceAIErrorScope.SERVICE,
            message='test error',
            url='https://example.com',
            status_code=403,
            payload_error='forbidden',
        )
        self.assertEqual(exc.error_scope, WorkforceAIErrorScope.SERVICE)
        self.assertEqual(exc.message, 'test error')
        self.assertEqual(exc.url, 'https://example.com')
        self.assertEqual(exc.status_code, 403)
        self.assertEqual(exc.payload_error, 'forbidden')

    def test_exception_str(self):
        exc = WorkforceAIApiException(
            error_scope=WorkforceAIErrorScope.NETWORKING,
            message='timeout',
        )
        s = str(exc)
        self.assertIn('NETWORKING', s)
        self.assertIn('timeout', s)

    def test_error_scopes(self):
        self.assertEqual(WorkforceAIErrorScope.NETWORKING.value, 'NETWORKING')
        self.assertEqual(WorkforceAIErrorScope.SERVICE.value, 'SERVICE')
        self.assertEqual(WorkforceAIErrorScope.SESSION.value, 'SESSION')
        self.assertEqual(WorkforceAIErrorScope.INVALID_PARAMS.value, 'INVALID_PARAMS')


# ────────────────────────────────────────────
# SDKConnectionState
# ────────────────────────────────────────────

class TestSDKConnectionState(unittest.TestCase):

    def test_all_states_exist(self):
        self.assertEqual(SDKConnectionState.CONNECTED.value, 'CONNECTED')
        self.assertEqual(SDKConnectionState.CONNECTING.value, 'CONNECTING')
        self.assertEqual(SDKConnectionState.DISCONNECTED.value, 'DISCONNECTED')
        self.assertEqual(SDKConnectionState.CONNECTION_ISSUE.value, 'CONNECTION_ISSUE')


# ────────────────────────────────────────────
# SessionManager connect failure handling
# ────────────────────────────────────────────

class TestSessionManagerConnectFailure(unittest.TestCase):

    def test_network_error_sets_connection_issue(self):
        from chkp_ai_security_sdk.core.session_manager import SessionManager
        sm = SessionManager()
        auth = InfinityPortalAuth(client_id='cid', access_key='key', gateway='https://nonexistent.invalid')
        with self.assertRaises(WorkforceAIApiException) as ctx:
            sm.connect(auth)
        self.assertEqual(ctx.exception.error_scope, WorkforceAIErrorScope.NETWORKING)
        self.assertEqual(sm.connection_state(), SDKConnectionState.CONNECTION_ISSUE)

    def test_bad_response_sets_connection_issue(self):
        from chkp_ai_security_sdk.core.session_manager import SessionManager
        sm = SessionManager()
        auth = InfinityPortalAuth(client_id='bad', access_key='bad', gateway='https://portal.checkpoint.com')

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'

        with patch('chkp_ai_security_sdk.core.session_manager.requests.post', return_value=mock_response):
            with self.assertRaises(WorkforceAIApiException) as ctx:
                sm.connect(auth)
        self.assertEqual(ctx.exception.error_scope, WorkforceAIErrorScope.SERVICE)
        self.assertEqual(ctx.exception.status_code, 401)
        self.assertEqual(sm.connection_state(), SDKConnectionState.CONNECTION_ISSUE)

    def test_unsuccessful_login_response(self):
        from chkp_ai_security_sdk.core.session_manager import SessionManager
        sm = SessionManager()
        auth = InfinityPortalAuth(client_id='cid', access_key='key', gateway='https://portal.checkpoint.com')

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"success": false}'
        mock_response.json.return_value = {'success': False}

        with patch('chkp_ai_security_sdk.core.session_manager.requests.post', return_value=mock_response):
            with self.assertRaises(WorkforceAIApiException) as ctx:
                sm.connect(auth)
        self.assertEqual(ctx.exception.error_scope, WorkforceAIErrorScope.SERVICE)
        self.assertEqual(sm.connection_state(), SDKConnectionState.CONNECTION_ISSUE)


if __name__ == '__main__':
    unittest.main()
