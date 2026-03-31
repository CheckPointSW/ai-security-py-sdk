"""AI Security SDK - async/await usage example.

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

load_dotenv()

from chkp_ai_security_sdk import AsyncAISecurity, InfinityPortalAuth


async def main():
    sdk = AsyncAISecurity()

    auth = InfinityPortalAuth(
        client_id=os.environ['CP_CI_CLIENT_ID'],
        access_key=os.environ['CP_CI_ACCESS_KEY'],
        gateway=os.environ['CP_CI_GATEWAY'],
    )

    print('Connecting...')
    await sdk.connect(auth)
    print('Connected!')

    try:
        # All API calls are awaitable
        print('\n--- Chats Policy Rulebase ---')
        result = await sdk.chats_policy_api.get_chats_rulebase_external_v1_chats_rulebase_get()
        print(result)

        # Run multiple API calls concurrently
        print('\n--- Concurrent API calls ---')
        access, dlp = await asyncio.gather(
            sdk.ai_access_policy_api.get_ai_access_rulebase_external_v1_ai_access_rulebase_get(),
            sdk.dlp_datatypes_api.get_predefined_datatypes_external_v1_dlp_datatypes_predefined_get(),
        )
        print(f'Access rules: {access}')
        print(f'DLP datatypes: {dlp}')
    finally:
        await sdk.disconnect()
        print('\nDisconnected.')


asyncio.run(main())
