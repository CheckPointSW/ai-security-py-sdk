# Check Point - AI Security Python SDK (Workforce AI + Browse Security)

[![License](https://img.shields.io/github/license/CheckPointSW/ai-security-py-sdk.svg?style=plastic)](https://github.com/CheckPointSW/ai-security-py-sdk/blob/release/LICENSE) [![Latest Release](https://img.shields.io/github/v/release/CheckPointSW/ai-security-py-sdk?style=plastic)](https://github.com/CheckPointSW/ai-security-py-sdk/releases) [![PyPI version](https://img.shields.io/pypi/v/chkp-ai-security-sdk.svg?style=plastic)](https://pypi.org/project/chkp-ai-security-sdk/)

[![Build SDK Package](https://github.com/CheckPointSW/ai-security-py-sdk/actions/workflows/build.yml/badge.svg)](https://github.com/CheckPointSW/ai-security-py-sdk/actions/workflows/build.yml) [![Publish package to PyPI](https://github.com/CheckPointSW/ai-security-py-sdk/actions/workflows/release.yml/badge.svg)](https://github.com/CheckPointSW/ai-security-py-sdk/actions/workflows/release.yml)

This is the official Check Point AI Security SDK for Python, covering both **Workforce AI** and **Browse Security** products.

The SDK is based on the public [AI Security OpenAPI](https://app.swaggerhub.com/apis/Check-Point/checkpoint-ai-security) and [Browse Security OpenAPI](https://app.swaggerhub.com/apis/Check-Point/checkpoint-browse-security) specifications.

With the SDK, you do not have to manage log in, send keep alive requests, or worry about session expiration.

> The SDK supports simultaneous instances with different tenants, and both products can be used independently or together.

## SDK installation

Via PIP (PyPi registry)
```bash
pip install chkp-ai-security-sdk
```

## Getting started

Import the SDK classes for the product(s) you need:

```python
from chkp_ai_security_sdk import AISecurity, BrowseSecurity
```

- **`AISecurity`** — Workforce AI Security (Chats policy, Access policy, Agents policy, etc.)
- **`BrowseSecurity`** — Browse Security (Secure Browsing policy, DLP policy, web access policy, etc.)

Each class manages its own session independently. Create an instance and provide CloudInfra API credentials to connect.

### Obtaining API credentials

1. Go to the [Infinity Portal API Keys page](https://portal.checkpoint.com/dashboard/settings/api-keys).
2. Click **New** > **New Account API Key**.
3. In the **Service** dropdown select:
   - **Workforce AI Security** for `AISecurity`
   - **Browser Security** for `BrowseSecurity`
4. Copy the **Client ID**, **Secret Key**, and **Authentication URL** (gateway).

For more information, see [Infinity Portal Administration Guide](https://sc1.checkpoint.com/documents/Infinity_Portal/WebAdminGuides/EN/Infinity-Portal-Admin-Guide/Content/Topics-Infinity-Portal/API-Keys.htm?tocpath=Global%20Settings%7C_____7#API_Keys).

### Available gateways

| Region | Gateway URL |
|---|---|
| Europe | `https://cloudinfra-gw.portal.checkpoint.com` |
| United States | `https://cloudinfra-gw-us.portal.checkpoint.com` |

Once the Client ID, Secret Key, and Authentication URL are obtained, the SDK can be used.

All API operations can be explored on SwaggerHub:
- [Workforce AI Security APIs](https://app.swaggerhub.com/apis/Check-Point/checkpoint-ai-security)
- [Browse Security APIs](https://app.swaggerhub.com/apis/Check-Point/checkpoint-browse-security)

### Workforce AI Security example

```python
from chkp_ai_security_sdk import AISecurity, InfinityPortalAuth

ai = AISecurity()
ai.connect(infinity_portal_auth=InfinityPortalAuth(
    client_id="your-client-id",
    access_key="your-secret-key",
    gateway="https://cloudinfra-gw-us.portal.checkpoint.com",
))

rulebase = ai.chats_policy_api.get_chats_rulebase_external_v1_chats_rulebase_get()
print(rulebase)

ai.disconnect()
```

### Browse Security example

```python
from chkp_ai_security_sdk import BrowseSecurity, InfinityPortalAuth

browse = BrowseSecurity()
browse.connect(infinity_portal_auth=InfinityPortalAuth(
    client_id="your-client-id",
    access_key="your-secret-key",
    gateway="https://cloudinfra-gw-us.portal.checkpoint.com",
))

rulebase = browse.dlp_policy_api.get_dlp_rulebase_external_v1_dlp_rulebase_get()
print(rulebase)

browse.disconnect()
```

### Using both products together

```python
from chkp_ai_security_sdk import AISecurity, BrowseSecurity, InfinityPortalAuth

auth = InfinityPortalAuth(
    client_id="your-client-id",
    access_key="your-secret-key",
    gateway="https://cloudinfra-gw-us.portal.checkpoint.com",
)

ai = AISecurity()
browse = BrowseSecurity()

ai.connect(infinity_portal_auth=auth)
browse.connect(infinity_portal_auth=auth)

# Workforce AI
chats = ai.chats_policy_api.get_chats_rulebase_external_v1_chats_rulebase_get()

# Browse Security
dlp = browse.dlp_policy_api.get_dlp_rulebase_external_v1_dlp_rulebase_get()

ai.disconnect()
browse.disconnect()
```

### Async support

The SDK provides async variants for both products:

```python
import asyncio
from chkp_ai_security_sdk import AsyncAISecurity, AsyncBrowseSecurity, InfinityPortalAuth

async def main():
    auth = InfinityPortalAuth(
        client_id="your-client-id",
        access_key="your-secret-key",
        gateway="https://cloudinfra-gw-us.portal.checkpoint.com",
    )

    ai = AsyncAISecurity()
    browse = AsyncBrowseSecurity()

    await asyncio.gather(ai.connect(auth), browse.connect(auth))

    # All API calls are awaitable
    chats = await ai.chats_policy_api.get_chats_rulebase_external_v1_chats_rulebase_get()
    dlp = await browse.dlp_policy_api.get_dlp_rulebase_external_v1_dlp_rulebase_get()

    await asyncio.gather(ai.disconnect(), browse.disconnect())

asyncio.run(main())
```

## Troubleshooting and logging

The full version and build info of the SDK is available via the `info()` static method on each class:
```python
from chkp_ai_security_sdk import AISecurity, BrowseSecurity

print(AISecurity.info())       # Workforce AI build info
print(BrowseSecurity.info())   # Browse Security build info
```

AI Security SDK uses the official python logger package for logging.

There are 3 loggers, for general info, errors and to inspect network.

As default they will be disabled, in order to enable logging, set to the `AI_SECURITY_SDK_LOGGER` environment variable the following string before loading the SDK:
```bash
AI_SECURITY_SDK_LOGGER="*"
```

And for a specific/s logger set the logger name followed by a comma as following:
```bash
AI_SECURITY_SDK_LOGGER="info,error,network"
```

or activate logger programmatically using SDK methods:
```python
from chkp_ai_security_sdk import activate_all_loggers, activate_info_logger, activate_error_logger, activate_network_logger
...
activate_all_loggers()    # Will activate all loggers
activate_info_logger()    # Will activate the info logger only
activate_error_logger()   # Will activate the error logger only
activate_network_logger() # Will activate the network logger only
```

## Report Bug

In case of an issue or a bug found in the SDK, please open an [issue](https://github.com/CheckPointSW/ai-security-py-sdk/issues).

## Contributors
- Haim Kastner - [haimk@checkpoint.com](mailto:haimk@checkpoint.com)
