"""AI Security SDK - async/await usage example.

Demonstrates both AsyncAISecurity and AsyncBrowseSecurity instances
sharing the same credentials but managing independent sessions.

Setup:
    cp .env.example .env   # fill in your credentials
    pip install chkp-ai-security-sdk python-dotenv

Run:
    python async_usage.py

Requires Python 3.9+.
"""
import asyncio
import os
from dotenv import load_dotenv

from chkp_ai_security_sdk.generated import CommonSetActiveRequest

load_dotenv()

from chkp_ai_security_sdk import AsyncAISecurity, AsyncBrowseSecurity, InfinityPortalAuth


async def main():
    auth = InfinityPortalAuth(
        client_id=os.environ['CP_CI_CLIENT_ID'],
        access_key=os.environ['CP_CI_ACCESS_KEY'],
        gateway=os.environ['CP_CI_GATEWAY'],
    )

    ai = AsyncAISecurity()
    browse = AsyncBrowseSecurity()

    print('Connecting...')
    await asyncio.gather(ai.connect(auth), browse.connect(auth))
    print('Connected!')

    try:
        # ── AI Security APIs ──

        print('\n=== AI Security ===')

        print('\n--- Chats Policy Rulebase ---')
        result = await ai.chats_policy_api.get_chats_rulebase_external_v1_chats_rulebase_get()
        print(result)


        # Run multiple AI Security calls concurrently
        print('\n--- Concurrent AI Security calls ---')
        access, dlp = await asyncio.gather(
            ai.ai_access_policy_api.get_ai_access_rulebase_external_v1_ai_access_rulebase_get(),
            ai.dlp_datatypes_api.get_predefined_datatypes_external_v1_dlp_datatypes_predefined_get(),
        )
        print(f'Access rules: {access}')
        print(f'DLP datatypes: {dlp}')

        # ── Browse Security APIs ──

        print('\n=== Browse Security ===')

        print('\n--- DLP Policy Rulebase ---')
        result = await browse.dlp_policy_api.get_dlp_rulebase_external_v1_dlp_rulebase_get()
        print(result)

        # Run multiple Browse Security calls concurrently
        print('\n--- Concurrent Browse Security calls ---')
        web_access, secure_browsing, objects = await asyncio.gather(
            browse.web_access_policy_api.get_web_access_rulebase_external_v1_web_access_rulebase_get(),
            browse.secure_browsing_policy_api.get_secure_browsing_rulebase_external_v1_secure_browsing_rulebase_get(),
            browse.objects_api.get_file_protection_objects_external_v1_objects_file_protection_get(),
        )
        print(f'Web access rules: {web_access}')
        print(f'Secure browsing rules: {secure_browsing}')
        print(f'File protection objects: {objects}')
    finally:
        await asyncio.gather(ai.disconnect(), browse.disconnect())
        print('\nDisconnected.')


asyncio.run(main())
