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
class TestBrowseIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from chkp_ai_security_sdk import BrowseSecurity, InfinityPortalAuth
        cls.browse = BrowseSecurity()
        cls.browse.connect(InfinityPortalAuth(
            client_id=CLIENT_ID,
            access_key=ACCESS_KEY,
            gateway=GATEWAY,
        ))

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'browse'):
            cls.browse.disconnect()

    # ── DLP Policy Rulebase ──

    def test_get_dlp_rulebase(self):
        rb = self.browse.dlp_policy_api.get_dlp_rulebase_external_v1_dlp_rulebase_get()
        self.assertIsNotNone(rb)

    # ── Web Access Rulebase ──

    def test_get_web_access_rulebase(self):
        rb = self.browse.web_access_policy_api.get_web_access_rulebase_external_v1_web_access_rulebase_get()
        self.assertIsNotNone(rb)

    # ── Secure Browsing Rulebase ──

    def test_get_secure_browsing_rulebase(self):
        rb = self.browse.secure_browsing_policy_api.get_secure_browsing_rulebase_external_v1_secure_browsing_rulebase_get()
        self.assertIsNotNone(rb)

    # ── DLP Datatypes ──

    def test_get_predefined_dlp_datatypes(self):
        datatypes = self.browse.dlp_datatypes_api.get_predefined_datatypes_external_v1_dlp_datatypes_predefined_get()
        self.assertIsNotNone(datatypes)

    def test_get_all_dlp_datatypes(self):
        datatypes = self.browse.dlp_datatypes_api.get_all_datatypes_external_v1_dlp_datatypes_all_get()
        self.assertIsNotNone(datatypes)

    # ── Objects ──

    def test_get_file_protection_objects(self):
        objects = self.browse.objects_api.get_file_protection_objects_external_v1_objects_file_protection_get()
        self.assertIsNotNone(objects)

    def test_get_domains_objects(self):
        objects = self.browse.objects_api.get_domains_objects_external_v1_objects_domains_get()
        self.assertIsNotNone(objects)

    # ── Connection State ──

    def test_connection_state(self):
        from chkp_ai_security_sdk import SDKConnectionState
        state = self.browse.connection_state()
        self.assertEqual(state, SDKConnectionState.CONNECTED)


if __name__ == '__main__':
    unittest.main()
