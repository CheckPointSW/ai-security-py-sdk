"""AI Security SDK - basic synchronous usage example.

Setup:
    cp .env.example .env   # fill in your credentials
    pip install chkp-ai-security-sdk python-dotenv

Run:
    python basic_usage.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

from chkp_ai_security_sdk import AISecurity, InfinityPortalAuth

sdk = AISecurity()

auth = InfinityPortalAuth(
    client_id=os.environ['CP_CI_CLIENT_ID'],
    access_key=os.environ['CP_CI_ACCESS_KEY'],
    gateway=os.environ['CP_CI_GATEWAY'],
)

print('Connecting...')
sdk.connect(auth)
print('Connected!')
print(f'SDK info: {AISecurity.info()}')

try:
    # Get chats policy rulebase
    print('\n--- Chats Policy Rulebase ---')
    result = sdk.chats_policy_api.get_chats_rulebase_external_v1_chats_rulebase_get()
    print(result)

    # Get access policy rulebase
    print('\n--- Access Policy Rulebase ---')
    result = sdk.ai_access_policy_api.get_ai_access_rulebase_external_v1_ai_access_rulebase_get()
    print(result)

    # Get predefined DLP datatypes
    print('\n--- Predefined DLP Datatypes ---')
    result = sdk.dlp_datatypes_api.get_predefined_datatypes_external_v1_dlp_datatypes_predefined_get()
    print(result)
finally:
    sdk.disconnect()
    print('\nDisconnected.')
