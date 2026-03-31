# Check Point - AI Security Python SDK

> **Draft** – This is a pre-release version of the SDK published for early testing. APIs and behavior may change before the official release.

<!-- TODO: Remove the above draft notice once the official release is published -->

[![License](https://img.shields.io/github/license/CheckPointSW/ai-security-py-sdk.svg?style=plastic)](https://github.com/CheckPointSW/ai-security-py-sdk/blob/release/LICENSE) [![Latest Release](https://img.shields.io/github/v/release/CheckPointSW/ai-security-py-sdk?style=plastic)](https://github.com/CheckPointSW/ai-security-py-sdk/releases) [![PyPI version](https://img.shields.io/pypi/v/chkp-ai-security-sdk.svg?style=plastic)](https://pypi.org/project/chkp-ai-security-sdk/)

[![Build SDK Package](https://github.com/CheckPointSW/ai-security-py-sdk/actions/workflows/build.yml/badge.svg)](https://github.com/CheckPointSW/ai-security-py-sdk/actions/workflows/build.yml) [![Publish package to PyPI](https://github.com/CheckPointSW/ai-security-py-sdk/actions/workflows/release.yml/badge.svg)](https://github.com/CheckPointSW/ai-security-py-sdk/actions/workflows/release.yml)

This is the AI Security SDK for Python ecosystem.

The SDK is based on the public [AI Security OpenAPI](https://app.swaggerhub.com/apis/Check-Point/checkpoint-ai-security) specifications.

With the SDK, you do not have to manage log in, send keep alive requests, or worry about session expiration.

> The AI Security SDK supports simultaneous instances with different tenants.

## SDK installation

To start using this SDK, add the SDK package to your project

Via PIP (PyPi registry)
```bash
pip install chkp-ai-security-sdk
```

## Getting started

First, import the `AISecurity` object from the package.

```python
from chkp_ai_security_sdk import AISecurity
```

Then, create a new instance of `AISecurity`, which provides CloudInfra API credentials and a gateway to connect to.

### Obtaining API credentials

1. Go to the [Infinity Portal API Keys page](https://portal.checkpoint.com/dashboard/settings/api-keys).
2. Click **New** > **New Account API Key**.
3. In the **Service** dropdown select **Workforce AI Security** and create the key.
4. Copy the **Client ID**, **Secret Key**, and **Authentication URL** (gateway).

For more information, see [Infinity Portal Administration Guide](https://sc1.checkpoint.com/documents/Infinity_Portal/WebAdminGuides/EN/Infinity-Portal-Admin-Guide/Content/Topics-Infinity-Portal/API-Keys.htm?tocpath=Global%20Settings%7C_____7#API_Keys).

### Available gateways

| Region | Gateway URL |
|---|---|
| Europe | `https://cloudinfra-gw.portal.checkpoint.com` |
| United States | `https://cloudinfra-gw-us.portal.checkpoint.com` |

Once the Client ID, Secret Key, and Authentication URL are obtained, AI Security SDK can be used.

All API operations can be explored with the `AISecurity` instance, notice to the documentation on each API operation, what and where are the arguments it requires.

All APIs can be also explored in [SwaggerHub](https://app.swaggerhub.com/apis/Check-Point/checkpoint-ai-security)

A complete example:

```python
from chkp_ai_security_sdk import AISecurity, InfinityPortalAuth

# Create a new instance of AISecurity (we do support multiple instances in parallel)
ai = AISecurity()

# Connect to AI Security service using CloudInfra API credentials
ai.connect(infinity_portal_auth=InfinityPortalAuth(
        client_id="place here your CI client-id",   # The "Client ID"
        access_key="place here your CI access-key", # The "Secret Key"
        gateway="https://cloudinfra-gw-us.portal.checkpoint.com" # The "Authentication URL" (without /auth/external)
        ))

# Query the API operations
rulebase = ai.chats_policy_api.get_chats_rulebase_external_v1_chats_rulebase_get()
print(rulebase)

# Once finish, disconnect to stop all background session management.
ai.disconnect()
```

### Async support

The SDK also provides an async variant for use in async Python applications:

```python
import asyncio
from chkp_ai_security_sdk import AsyncAISecurity, InfinityPortalAuth

async def main():
    ai = AsyncAISecurity()
    await ai.connect(infinity_portal_auth=InfinityPortalAuth(
        client_id="your-client-id",
        access_key="your-secret-key",
        gateway="https://cloudinfra-gw-us.portal.checkpoint.com",
    ))

    # API calls are awaitable and run without blocking the event loop
    rulebase = await ai.chats_policy_api.get_chats_rulebase_external_v1_chats_rulebase_get()
    print(rulebase)

    await ai.disconnect()

asyncio.run(main())
```

## Troubleshooting and logging

The full version and build info of the SDK is available by `AISecurity.info()` see example:
```python
from chkp_ai_security_sdk import AISecurity, WorkforceAISDKInfo

sdk_info: WorkforceAISDKInfo = AISecurity.info()
print(sdk_info) # sdk_build:"9728283", sdk_version:"1.0.0", spec:"checkpoint-ai-security", spec_version:"1.0.0", released_on:"2024-01-01T00:00:00"
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

## All Check Point AI Security API tools

| Tool | Package |
|---|---|
| Python SDK | [`chkp-ai-security-sdk`](https://pypi.org/project/chkp-ai-security-sdk/) |
| JS/TS SDK | [`@chkp/ai-security-sdk`](https://www.npmjs.com/package/@chkp/ai-security-sdk) |
| OpenAPI Spec | [SwaggerHub](https://app.swaggerhub.com/apis/Check-Point/checkpoint-ai-security) |

## Report Bug

In case of an issue or a bug found in the SDK, please open an [issue](https://github.com/CheckPointSW/ai-security-py-sdk/issues).

## Contributors
- Haim Kastner - [haimk@checkpoint.com](mailto:haimk@checkpoint.com)
