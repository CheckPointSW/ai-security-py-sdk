import asyncio
import unittest
import os

CLIENT_ID = os.environ.get('CP_CI_CLIENT_ID', '')
ACCESS_KEY = os.environ.get('CP_CI_ACCESS_KEY', '')
GATEWAY = os.environ.get('CP_CI_GATEWAY', '')

CREDS_AVAILABLE = bool(CLIENT_ID and ACCESS_KEY and GATEWAY)


def skip_without_creds(cls):
    if not CREDS_AVAILABLE:
        return unittest.skip('CP_CI_* credentials not set')(cls)
    return cls


@skip_without_creds
class TestAsyncBrowseIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from chkp_ai_security_sdk import AsyncBrowseSecurity, InfinityPortalAuth
        cls.browse = AsyncBrowseSecurity()
        asyncio.get_event_loop().run_until_complete(
            cls.browse.connect(InfinityPortalAuth(
                client_id=CLIENT_ID,
                access_key=ACCESS_KEY,
                gateway=GATEWAY,
            ))
        )

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'browse'):
            asyncio.get_event_loop().run_until_complete(cls.browse.disconnect())

    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    # ── DLP Policy Rulebase ──

    def test_get_dlp_rulebase(self):
        async def _test():
            rb = await self.browse.dlp_policy_api.get_dlp_rulebase_external_v1_dlp_rulebase_get()
            self.assertIsNotNone(rb)
        self._run(_test())

    # ── Web Access Rulebase ──

    def test_get_web_access_rulebase(self):
        async def _test():
            rb = await self.browse.web_access_policy_api.get_web_access_rulebase_external_v1_web_access_rulebase_get()
            self.assertIsNotNone(rb)
        self._run(_test())

    # ── Secure Browsing Rulebase ──

    def test_get_secure_browsing_rulebase(self):
        async def _test():
            rb = await self.browse.secure_browsing_policy_api.get_secure_browsing_rulebase_external_v1_secure_browsing_rulebase_get()
            self.assertIsNotNone(rb)
        self._run(_test())

    # ── DLP Datatypes ──

    def test_get_predefined_dlp_datatypes(self):
        async def _test():
            datatypes = await self.browse.dlp_datatypes_api.get_predefined_datatypes_external_v1_dlp_datatypes_predefined_get()
            self.assertIsNotNone(datatypes)
        self._run(_test())

    def test_get_all_dlp_datatypes(self):
        async def _test():
            datatypes = await self.browse.dlp_datatypes_api.get_all_datatypes_external_v1_dlp_datatypes_all_get()
            self.assertIsNotNone(datatypes)
        self._run(_test())

    # ── Objects ──

    def test_get_file_protection_objects(self):
        async def _test():
            objects = await self.browse.objects_api.get_file_protection_objects_external_v1_objects_file_protection_get()
            self.assertIsNotNone(objects)
        self._run(_test())

    def test_get_domains_objects(self):
        async def _test():
            objects = await self.browse.objects_api.get_domains_objects_external_v1_objects_domains_get()
            self.assertIsNotNone(objects)
        self._run(_test())

    # ── Connection State ──

    def test_connection_state(self):
        from chkp_ai_security_sdk import SDKConnectionState
        state = self.browse.connection_state()
        self.assertEqual(state, SDKConnectionState.CONNECTED)

    # ── Concurrent Requests ──

    def test_concurrent_requests(self):
        async def _test():
            dlp_rb, web_rb, sb_rb = await asyncio.gather(
                self.browse.dlp_policy_api.get_dlp_rulebase_external_v1_dlp_rulebase_get(),
                self.browse.web_access_policy_api.get_web_access_rulebase_external_v1_web_access_rulebase_get(),
                self.browse.secure_browsing_policy_api.get_secure_browsing_rulebase_external_v1_secure_browsing_rulebase_get(),
            )
            self.assertIsNotNone(dlp_rb)
            self.assertIsNotNone(web_rb)
            self.assertIsNotNone(sb_rb)
        self._run(_test())


if __name__ == '__main__':
    unittest.main()
