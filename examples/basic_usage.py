"""AI Security SDK - basic synchronous usage example.

Demonstrates both AISecurity (Workforce AI) and BrowseSecurity instances
sharing the same credentials but managing independent sessions.

Setup:
    cp .env.example .env   # fill in your credentials
    pip install chkp-ai-security-sdk python-dotenv

Run:
    python basic_usage.py
"""
import os
from dotenv import load_dotenv

from chkp_ai_security_sdk.generated import CommonSetActiveRequest

load_dotenv()

from chkp_ai_security_sdk import AISecurity, BrowseSecurity, InfinityPortalAuth

auth = InfinityPortalAuth(
    client_id=os.environ['CP_CI_CLIENT_ID'],
    access_key=os.environ['CP_CI_ACCESS_KEY'],
    gateway=os.environ['CP_CI_GATEWAY'],
)

ai = AISecurity()
browse = BrowseSecurity()

print('Connecting...')
ai.connect(auth)
browse.connect(auth)
print('Connected!')
print(f'AI Security info: {AISecurity.info()}')
print(f'Browse Security info: {BrowseSecurity.info()}')

try:
    # ── AI Security APIs ──

    print('\n=== AI Security ===')

    print('\n--- Chats Policy Rulebase ---')
    result = ai.chats_policy_api.get_chats_rulebase_external_v1_chats_rulebase_get()
    print(result)

    ai.rulebase_api.set_active_external_v1_rules_set_active_put(CommonSetActiveRequest(
        rule_id=result.rules[0].rule_id,
        active=True,
    ))
    print('\n--- Access Policy Rulebase ---')
    result = ai.ai_access_policy_api.get_ai_access_rulebase_external_v1_ai_access_rulebase_get()
    print(result)

    print('\n--- Predefined DLP Datatypes ---')
    result = ai.dlp_datatypes_api.get_predefined_datatypes_external_v1_dlp_datatypes_predefined_get()
    print(result)

    # ── Browse Security APIs ──

    print('\n=== Browse Security ===')

    print('\n--- DLP Policy Rulebase ---')
    result = browse.dlp_policy_api.get_dlp_rulebase_external_v1_dlp_rulebase_get()
    print(result)

    print('\n--- Web Access Rulebase ---')
    result = browse.web_access_policy_api.get_web_access_rulebase_external_v1_web_access_rulebase_get()
    print(result)

    print('\n--- Secure Browsing Rulebase ---')
    result = browse.secure_browsing_policy_api.get_secure_browsing_rulebase_external_v1_secure_browsing_rulebase_get()
    print(result)

    print('\n--- File Protection Objects ---')
    result = browse.objects_api.get_file_protection_objects_external_v1_objects_file_protection_get()
    print(result)
finally:
    ai.disconnect()
    browse.disconnect()
    print('\nDisconnected.')
