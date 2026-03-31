import os
import re
import shutil
import json
from datetime import datetime
from pathlib import Path

PROJECT_DIR = str(Path(os.path.dirname(__file__), '..', '..'))
BASE_PATH = os.path.join(PROJECT_DIR, 'chkp_ai_security_sdk')
OUTPUT_PATH = os.path.join(BASE_PATH, 'generated')
SPEC_PATH = os.path.join(PROJECT_DIR, 'resources', 'specs', 'main')

# SDK configuration
PKG_NAME = 'chkp_ai_security_sdk'


def __prepare_build_info():
    with open(os.path.join(SPEC_PATH, 'swagger.json'), 'r') as f:
        swagger_spec = json.load(f)
    with open(os.path.join(SPEC_PATH, 'spec'), 'r') as f:
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
    with open(os.path.join(OUTPUT_PATH, 'sdk_build.py'), 'w') as f:
        f.write(content)
    print('[post-build] sdk_build.py written')


def __discover_apis():
    """Scan generated api/__init__.py to discover all API classes."""
    init_path = os.path.join(OUTPUT_PATH, 'api', '__init__.py')
    apis = []
    with open(init_path, 'r') as f:
        for line in f:
            m = re.match(r'from \S+\.api\.(\w+) import (\w+)', line)
            if m:
                apis.append((m.group(1), m.group(2)))
    return sorted(apis, key=lambda x: x[0])


def __generate_api_mixin(apis):
    """Generate generated/api_mixin.py with API property accessors."""
    props = ''
    for module_name, class_name in apis:
        props += f'''
    @property
    def {module_name}(self):
        from {PKG_NAME}.generated.api.{module_name} import {class_name}
        return {class_name}(self._get_api_client())
'''

    content = f'''"""Auto-generated API mixin — do not edit manually.

Provides property accessors for all generated API classes.
Inherit from _ApiMixin in your SDK class and implement _get_api_client().
"""


class _ApiMixin:
    def _get_api_client(self):
        raise NotImplementedError
{props}'''

    with open(os.path.join(OUTPUT_PATH, 'api_mixin.py'), 'w') as f:
        f.write(content)
    print(f'[post-build] api_mixin.py generated with {len(apis)} APIs')


def __cleanup_generated():
    for dirname in ['test', 'docs']:
        path = os.path.join(OUTPUT_PATH, dirname)
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f'[post-build] Removed {path}')
    # Clean test dir at project root if generator created one
    test_root = os.path.join(PROJECT_DIR, 'test')
    if os.path.exists(test_root):
        shutil.rmtree(test_root)
    # Remove generated README files
    for readme_name in ['generated_README.md', 'README.md']:
        readme_path = os.path.join(BASE_PATH, readme_name)
        if os.path.exists(readme_path):
            os.remove(readme_path)
            print(f'[post-build] Removed {readme_path}')


def post_build_process():
    print('[post-build] Preparing build info...')
    __prepare_build_info()
    print('[post-build] Cleaning up generated files...')
    __cleanup_generated()
    print('[post-build] Discovering APIs...')
    apis = __discover_apis()
    print(f'[post-build] Found {len(apis)} APIs: {", ".join(c for _, c in apis)}')
    print('[post-build] Generating API mixin...')
    __generate_api_mixin(apis)
    print('[post-build] Setting __init__ export...')
    shutil.copy(
        os.path.join(BASE_PATH, '__init__template.py'),
        os.path.join(BASE_PATH, '__init__.py'),
    )
    print('[post-build] Done.')
