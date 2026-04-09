import os
import re
import shutil
import json
from datetime import datetime
from pathlib import Path

PROJECT_DIR = str(Path(os.path.dirname(__file__), '..', '..'))
BASE_PATH = os.path.join(PROJECT_DIR, 'chkp_ai_security_sdk')

# SDK configuration — one entry per product
PKG_NAME = 'chkp_ai_security_sdk'

PRODUCTS = [
    # ── Sync ──
    {
        'label': 'ai-security',
        'generated_dir': os.path.join(BASE_PATH, 'generated'),
        'spec_dir': os.path.join(PROJECT_DIR, 'resources', 'specs', 'main'),
        'pkg_prefix': f'{PKG_NAME}.generated',
        'mixin_class': '_ApiMixin',
    },
    {
        'label': 'browse-security',
        'generated_dir': os.path.join(BASE_PATH, 'generated_browse'),
        'spec_dir': os.path.join(PROJECT_DIR, 'resources', 'specs', 'browse'),
        'pkg_prefix': f'{PKG_NAME}.generated_browse',
        'mixin_class': '_BrowseApiMixin',
    },
    # ── Async ──
    {
        'label': 'ai-security-async',
        'generated_dir': os.path.join(BASE_PATH, 'generated_async'),
        'spec_dir': os.path.join(PROJECT_DIR, 'resources', 'specs', 'main'),
        'pkg_prefix': f'{PKG_NAME}.generated_async',
        'mixin_class': '_AsyncApiMixin',
    },
    {
        'label': 'browse-security-async',
        'generated_dir': os.path.join(BASE_PATH, 'generated_browse_async'),
        'spec_dir': os.path.join(PROJECT_DIR, 'resources', 'specs', 'browse'),
        'pkg_prefix': f'{PKG_NAME}.generated_browse_async',
        'mixin_class': '_AsyncBrowseApiMixin',
    },
]


def __prepare_build_info(product):
    output_path = product['generated_dir']
    spec_path = product['spec_dir']

    with open(os.path.join(spec_path, 'swagger.json'), 'r') as f:
        swagger_spec = json.load(f)
    with open(os.path.join(spec_path, 'spec'), 'r') as f:
        spec_name = f.readline().strip()

    sdk_build = os.environ.get('BUILD_JOB_ID', '')
    sdk_version = os.environ.get('BUILD_VERSION', '')
    spec_version = swagger_spec['info']['version']
    released_on = datetime.now().isoformat()

    content = f'''
from {PKG_NAME}.classes.workforceai_sdk_info import WorkforceAISDKInfo

def sdk_build_info() -> WorkforceAISDKInfo:
    return WorkforceAISDKInfo(
        sdk_build="{sdk_build}",
        sdk_version="{sdk_version}",
        spec="{spec_name}",
        spec_version="{spec_version}",
        released_on="{released_on}",
    )
'''
    with open(os.path.join(output_path, 'sdk_build.py'), 'w') as f:
        f.write(content)
    print(f'[post-build:{product["label"]}] sdk_build.py written')


def __discover_apis(product):
    """Scan generated api/__init__.py to discover all API classes."""
    init_path = os.path.join(product['generated_dir'], 'api', '__init__.py')
    apis = []
    with open(init_path, 'r') as f:
        for line in f:
            m = re.match(r'from \S+\.api\.(\w+) import (\w+)', line)
            if m:
                apis.append((m.group(1), m.group(2)))
    return sorted(apis, key=lambda x: x[0])


def __generate_api_mixin(product, apis):
    """Generate generated/api_mixin.py with API property accessors."""
    pkg_prefix = product['pkg_prefix']
    mixin_class = product['mixin_class']

    props = ''
    for module_name, class_name in apis:
        props += f'''
    @property
    def {module_name}(self):
        from {pkg_prefix}.api.{module_name} import {class_name}
        return {class_name}(self._get_api_client())
'''

    content = f'''"""Auto-generated API mixin — do not edit manually.

Provides property accessors for all generated API classes.
Inherit from {mixin_class} in your SDK class and implement _get_api_client().
"""


class {mixin_class}:
    def _get_api_client(self):
        raise NotImplementedError
{props}'''

    with open(os.path.join(product['generated_dir'], 'api_mixin.py'), 'w') as f:
        f.write(content)
    print(f'[post-build:{product["label"]}] api_mixin.py generated with {len(apis)} APIs')


def __cleanup_generated(product):
    output_path = product['generated_dir']
    for dirname in ['test', 'docs']:
        path = os.path.join(output_path, dirname)
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f'[post-build:{product["label"]}] Removed {path}')
    # Clean test dir at project root if generator created one
    test_root = os.path.join(PROJECT_DIR, 'test')
    if os.path.exists(test_root):
        shutil.rmtree(test_root)
    # Remove generated README files
    for readme_name in ['generated_README.md', 'README.md']:
        readme_path = os.path.join(BASE_PATH, readme_name)
        if os.path.exists(readme_path):
            os.remove(readme_path)
            print(f'[post-build:{product["label"]}] Removed {readme_path}')


def __inject_api_source_header(product):
    """Inject x-api-source default header into generated api_client.py."""
    api_client_path = os.path.join(product['generated_dir'], 'api_client.py')
    if not os.path.exists(api_client_path):
        return
    with open(api_client_path, 'r') as f:
        content = f.read()
    needle = "self.default_headers = {}"
    if needle in content and 'x-api-source' not in content:
        content = content.replace(needle, "self.default_headers = {'x-api-source': 'py_sdk'}")
        with open(api_client_path, 'w') as f:
            f.write(content)
        print(f'[post-build:{product["label"]}] Injected x-api-source header into api_client.py')


def post_build_process():
    for product in PRODUCTS:
        label = product['label']
        print(f'[post-build:{label}] Preparing build info...')
        __prepare_build_info(product)
        print(f'[post-build:{label}] Cleaning up generated files...')
        __cleanup_generated(product)
        print(f'[post-build:{label}] Injecting x-api-source header...')
        __inject_api_source_header(product)
        print(f'[post-build:{label}] Discovering APIs...')
        apis = __discover_apis(product)
        print(f'[post-build:{label}] Found {len(apis)} APIs: {", ".join(c for _, c in apis)}')
        print(f'[post-build:{label}] Generating API mixin...')
        __generate_api_mixin(product, apis)

    print('[post-build] Setting __init__ export...')
    shutil.copy(
        os.path.join(BASE_PATH, '__init__template.py'),
        os.path.join(BASE_PATH, '__init__.py'),
    )
    print('[post-build] Done.')
