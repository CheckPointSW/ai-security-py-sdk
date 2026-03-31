import unittest
import os
import time

CLIENT_ID = os.environ.get('CP_CI_CLIENT_ID', '')
ACCESS_KEY = os.environ.get('CP_CI_ACCESS_KEY', '')
GATEWAY = os.environ.get('CP_CI_GATEWAY', '')

CREDS_AVAILABLE = bool(CLIENT_ID and ACCESS_KEY and GATEWAY)


def skip_without_creds(cls):
    if not CREDS_AVAILABLE:
        return unittest.skip('CP_CI_* credentials not set')(cls)
    return cls


@skip_without_creds
class TestIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from chkp_ai_security_sdk import AISecurity, InfinityPortalAuth
        cls.ai = AISecurity()
        cls.ai.connect(InfinityPortalAuth(
            client_id=CLIENT_ID,
            access_key=ACCESS_KEY,
            gateway=GATEWAY,
        ))
        cls._cleanup_all()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'ai'):
            cls._cleanup_all()
            cls.ai.disconnect()

    @classmethod
    def _cleanup_all(cls):
        for get_rulebase in [
            cls.ai.chats_policy_api.get_chats_rulebase_external_v1_chats_rulebase_get,
            cls.ai.ai_access_policy_api.get_ai_access_rulebase_external_v1_ai_access_rulebase_get,
            cls.ai.agents_policy_api.get_agents_rulebase_external_v1_agents_rulebase_get,
        ]:
            try:
                rb = get_rulebase()
                for rule in rb.rules:
                    try:
                        cls.ai.rulebase_api.delete_rule_external_v1_rules_rule_id_delete(rule.rule_id)
                    except Exception:
                        pass
            except Exception:
                pass

        time.sleep(2)

    # ── GenAI Chats Rule CRUD ──

    def test_genai_chats_rule_crud(self):
        from chkp_ai_security_sdk.generated.models.add_chats_rule_request import AddChatsRuleRequest
        from chkp_ai_security_sdk.generated.models.chats_policy import ChatsPolicy
        from chkp_ai_security_sdk.generated.models.services_and_application import ServicesAndApplication
        from chkp_ai_security_sdk.generated.models.selection_mode import SelectionMode
        from chkp_ai_security_sdk.generated.models.data_type import DataType
        from chkp_ai_security_sdk.generated.models.dlp_type import DLPType
        from chkp_ai_security_sdk.generated.models.dlp_event_type import DLPEventType
        from chkp_ai_security_sdk.generated.models.logging_status import LoggingStatus
        from chkp_ai_security_sdk.generated.models.assignment import Assignment
        from chkp_ai_security_sdk.generated.models.assignment_type import AssignmentType
        from chkp_ai_security_sdk.generated.models.common_set_info_request import CommonSetInfoRequest
        from chkp_ai_security_sdk.generated.models.common_set_active_request import CommonSetActiveRequest
        from chkp_ai_security_sdk.generated.models.patch_chats_policy_request import PatchChatsPolicyRequest

        # CREATE
        result = self.ai.chats_policy_api.add_chats_rule_external_v1_chats_rule_post(
            add_chats_rule_request=AddChatsRuleRequest(
                name='Test DLP Rule',
                description='Integration test',
                order=0,
                policy=ChatsPolicy(
                    event_type=DLPEventType.FILE_UPLOAD,
                    action='prevent',
                    logging=LoggingStatus.ENABLED,
                    services_and_application=ServicesAndApplication(mode=SelectionMode.ALL),
                    data_types=[DataType(
                        id='cf0523c1-537e-4a4b-8bb8-084b7b9e0b45',
                        name='Credit Card Number',
                        type=DLPType.PRE_DEFINED,
                    )],
                ),
                source=[Assignment(
                    assignment_id='entire-org',
                    display_name='Entire Organization',
                    assignment_type=AssignmentType.ASSIGNMENT_TYPE_ENTIRE_ORG,
                )],
            ),
        )
        rule_id = result.rule_id
        self.assertTrue(rule_id)

        # READ
        rb = self.ai.chats_policy_api.get_chats_rulebase_external_v1_chats_rulebase_get()
        rule = next(r for r in rb.rules if r.rule_id == rule_id)
        self.assertEqual(rule.name, 'Test DLP Rule')
        self.assertTrue(rule.active)

        # UPDATE info
        self.ai.rulebase_api.set_rule_info_external_v1_rules_set_info_put(
            CommonSetInfoRequest(
                rule_id=rule_id,
                name='Test DLP Rule Updated',
                description='Updated',
            ),
        )
        rb2 = self.ai.chats_policy_api.get_chats_rulebase_external_v1_chats_rulebase_get()
        rule2 = next(r for r in rb2.rules if r.rule_id == rule_id)
        self.assertEqual(rule2.name, 'Test DLP Rule Updated')
        self.assertEqual(rule2.description, 'Updated')

        # PATCH policy
        self.ai.chats_policy_api.patch_chats_policy_external_v1_chats_rule_patch_policy_patch(
            PatchChatsPolicyRequest(
                rule_id=rule_id,
                policy=ChatsPolicy(action='detect'),
            ),
        )
        rb3 = self.ai.chats_policy_api.get_chats_rulebase_external_v1_chats_rulebase_get()
        rule3 = next(r for r in rb3.rules if r.rule_id == rule_id)
        self.assertEqual(rule3.policy.action, 'detect')

        # DISABLE
        self.ai.rulebase_api.set_active_external_v1_rules_set_active_put(
            CommonSetActiveRequest(rule_id=rule_id, active=False),
        )
        rb4 = self.ai.chats_policy_api.get_chats_rulebase_external_v1_chats_rulebase_get()
        rule4 = next(r for r in rb4.rules if r.rule_id == rule_id)
        self.assertFalse(rule4.active)

        # DELETE
        self.ai.rulebase_api.delete_rule_external_v1_rules_rule_id_delete(rule_id)
        rb5 = self.ai.chats_policy_api.get_chats_rulebase_external_v1_chats_rulebase_get()
        self.assertFalse(any(r.rule_id == rule_id for r in rb5.rules))

    # ── GenAI Access Rule CRUD ──

    def test_genai_access_rule_crud(self):
        from chkp_ai_security_sdk.generated.models.add_access_rule_request import AddAccessRuleRequest
        from chkp_ai_security_sdk.generated.models.access_policy import AccessPolicy
        from chkp_ai_security_sdk.generated.models.services_and_application import ServicesAndApplication
        from chkp_ai_security_sdk.generated.models.selection_mode import SelectionMode
        from chkp_ai_security_sdk.generated.models.gen_ai_app import GenAIApp
        from chkp_ai_security_sdk.generated.models.account_selection_mode import AccountSelectionMode
        from chkp_ai_security_sdk.generated.models.logging_status import LoggingStatus
        from chkp_ai_security_sdk.generated.models.assignment import Assignment
        from chkp_ai_security_sdk.generated.models.assignment_type import AssignmentType
        from chkp_ai_security_sdk.generated.models.common_set_info_request import CommonSetInfoRequest

        # CREATE
        result = self.ai.ai_access_policy_api.add_ai_access_rule_external_v1_ai_access_rule_post(
            add_access_rule_request=AddAccessRuleRequest(
                name='Test Access Rule',
                description='Integration test',
                order=0,
                policy=AccessPolicy(
                    action='block',
                    logging=LoggingStatus.ENABLED,
                    services_and_application=ServicesAndApplication(
                        mode=SelectionMode.SELECTED,
                        genai_application=[GenAIApp(id=1, mode=AccountSelectionMode.ALL)],
                    ),
                ),
                source=[Assignment(
                    assignment_id='entire-org',
                    display_name='Entire Organization',
                    assignment_type=AssignmentType.ASSIGNMENT_TYPE_ENTIRE_ORG,
                )],
            ),
        )
        rule_id = result.rule_id
        self.assertTrue(rule_id)

        # READ
        rb = self.ai.ai_access_policy_api.get_ai_access_rulebase_external_v1_ai_access_rulebase_get()
        rule = next(r for r in rb.rules if r.rule_id == rule_id)
        self.assertEqual(rule.name, 'Test Access Rule')

        # UPDATE info
        self.ai.rulebase_api.set_rule_info_external_v1_rules_set_info_put(
            CommonSetInfoRequest(
                rule_id=rule_id,
                name='Test Access Rule v2',
                description='v2',
            ),
        )
        rb2 = self.ai.ai_access_policy_api.get_ai_access_rulebase_external_v1_ai_access_rulebase_get()
        rule2 = next(r for r in rb2.rules if r.rule_id == rule_id)
        self.assertEqual(rule2.name, 'Test Access Rule v2')

        # DELETE
        self.ai.rulebase_api.delete_rule_external_v1_rules_rule_id_delete(rule_id)
        rb3 = self.ai.ai_access_policy_api.get_ai_access_rulebase_external_v1_ai_access_rulebase_get()
        self.assertFalse(any(r.rule_id == rule_id for r in rb3.rules))

    # ── GenAI Agents Rule CRUD ──

    def test_genai_agents_rule_crud(self):
        from chkp_ai_security_sdk.generated.models.add_mcp_server_rule_request import AddMCPServerRuleRequest
        from chkp_ai_security_sdk.generated.models.agents_policy import AgentsPolicy
        from chkp_ai_security_sdk.generated.models.mcp_clients import MCPClients
        from chkp_ai_security_sdk.generated.models.mcp_servers import MCPServers
        from chkp_ai_security_sdk.generated.models.mcp_servers_mode import MCPServersMode
        from chkp_ai_security_sdk.generated.models.tooling import Tooling
        from chkp_ai_security_sdk.generated.models.match_tools_mode import MatchToolsMode
        from chkp_ai_security_sdk.generated.models.selection_mode import SelectionMode
        from chkp_ai_security_sdk.generated.models.logging_status import LoggingStatus
        from chkp_ai_security_sdk.generated.models.assignment import Assignment
        from chkp_ai_security_sdk.generated.models.assignment_type import AssignmentType

        # CREATE
        result = self.ai.agents_policy_api.add_agents_rule_external_v1_agents_rule_post(
            add_mcp_server_rule_request=AddMCPServerRuleRequest(
                name='Test Agents Rule',
                description='Integration test',
                order=0,
                policy=AgentsPolicy(
                    action='allow',
                    logging=LoggingStatus.ENABLED,
                    clients=MCPClients(mode=SelectionMode.ALL),
                    servers=MCPServers(mcp_servers_mode=MCPServersMode.ALL),
                    tooling=Tooling(match_mode=MatchToolsMode.TOOLS_INCLUDE),
                ),
                source=[Assignment(
                    assignment_id='entire-org',
                    display_name='Entire Organization',
                    assignment_type=AssignmentType.ASSIGNMENT_TYPE_ENTIRE_ORG,
                )],
            ),
        )
        rule_id = result.rule_id
        self.assertTrue(rule_id)

        # READ
        rb = self.ai.agents_policy_api.get_agents_rulebase_external_v1_agents_rulebase_get()
        rule = next(r for r in rb.rules if r.rule_id == rule_id)
        self.assertEqual(rule.name, 'Test Agents Rule')

        # DELETE
        self.ai.rulebase_api.delete_rule_external_v1_rules_rule_id_delete(rule_id)

    # ── Get Rulebase ──

    def test_get_chats_rulebase(self):
        rb = self.ai.chats_policy_api.get_chats_rulebase_external_v1_chats_rulebase_get()
        self.assertIsNotNone(rb)
        self.assertIsInstance(rb.rules, list)
        self.assertIsInstance(rb.rulebase_version, int)

    def test_get_access_rulebase(self):
        rb = self.ai.ai_access_policy_api.get_ai_access_rulebase_external_v1_ai_access_rulebase_get()
        self.assertIsNotNone(rb)
        self.assertIsInstance(rb.rules, list)

    def test_get_agents_rulebase(self):
        rb = self.ai.agents_policy_api.get_agents_rulebase_external_v1_agents_rulebase_get()
        self.assertIsNotNone(rb)
        self.assertIsInstance(rb.rules, list)

    # ── DLP Datatypes ──

    def test_get_predefined_dlp_datatypes(self):
        datatypes = self.ai.dlp_datatypes_api.get_predefined_datatypes_external_v1_dlp_datatypes_predefined_get()
        self.assertIsNotNone(datatypes)

    def test_get_all_dlp_datatypes(self):
        datatypes = self.ai.dlp_datatypes_api.get_all_datatypes_external_v1_dlp_datatypes_all_get()
        self.assertIsNotNone(datatypes)

    # ── SetActive Toggle ──

    def test_set_active_toggle(self):
        from chkp_ai_security_sdk.generated.models.add_chats_rule_request import AddChatsRuleRequest
        from chkp_ai_security_sdk.generated.models.chats_policy import ChatsPolicy
        from chkp_ai_security_sdk.generated.models.services_and_application import ServicesAndApplication
        from chkp_ai_security_sdk.generated.models.selection_mode import SelectionMode
        from chkp_ai_security_sdk.generated.models.dlp_event_type import DLPEventType
        from chkp_ai_security_sdk.generated.models.logging_status import LoggingStatus
        from chkp_ai_security_sdk.generated.models.common_set_active_request import CommonSetActiveRequest

        result = self.ai.chats_policy_api.add_chats_rule_external_v1_chats_rule_post(
            add_chats_rule_request=AddChatsRuleRequest(
                name='Toggle Test Rule',
                order=0,
                policy=ChatsPolicy(
                    event_type=DLPEventType.PROMPT,
                    action='detect',
                    logging=LoggingStatus.ENABLED,
                    services_and_application=ServicesAndApplication(mode=SelectionMode.ALL),
                ),
            ),
        )
        rule_id = result.rule_id

        try:
            # Disable
            self.ai.rulebase_api.set_active_external_v1_rules_set_active_put(
                CommonSetActiveRequest(rule_id=rule_id, active=False),
            )
            rb = self.ai.chats_policy_api.get_chats_rulebase_external_v1_chats_rulebase_get()
            rule = next(r for r in rb.rules if r.rule_id == rule_id)
            self.assertFalse(rule.active)

            # Re-enable
            self.ai.rulebase_api.set_active_external_v1_rules_set_active_put(
                CommonSetActiveRequest(rule_id=rule_id, active=True),
            )
            rb2 = self.ai.chats_policy_api.get_chats_rulebase_external_v1_chats_rulebase_get()
            rule2 = next(r for r in rb2.rules if r.rule_id == rule_id)
            self.assertTrue(rule2.active)
        finally:
            self.ai.rulebase_api.delete_rule_external_v1_rules_rule_id_delete(rule_id)

    # ── Connection State ──

    def test_connection_state(self):
        from chkp_ai_security_sdk import SDKConnectionState
        state = self.ai.connection_state()
        self.assertEqual(state, SDKConnectionState.CONNECTED)


if __name__ == '__main__':
    unittest.main()
