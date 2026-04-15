import os
import re
import json
import shutil
import requests
from urllib.parse import urlparse

API_SPEC_OWNER = 'Check-Point'
SWAGGERHUB_API_KEY = os.environ.get('SWAGGERHUB_API_KEY')

BRANCH_NAME = os.environ.get('CI_COMMIT_REF_NAME') or os.environ.get('BRANCH_NAME')
print(f'[fetch-api] Branch: {BRANCH_NAME}, Build: {os.environ.get("BUILD_JOB_ID")}')

swagger_headers = {'Content-Type': 'application/json'}
if SWAGGERHUB_API_KEY:
    swagger_headers['Authorization'] = f'Bearer {SWAGGERHUB_API_KEY}'

OUTPUT_BASE_PATH = 'resources/specs'
SWAGGER_CONF = 'swagger.json'

ALLOWED_SPEC_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')


def __validate_spec_name(name):
    if not ALLOWED_SPEC_PATTERN.match(name):
        raise ValueError(f'Invalid spec name "{name}": must be alphanumeric, hyphens, or underscores only')
    return name


def __validate_local_path(local_path):
    real = os.path.realpath(local_path)
    project_root = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if not real.startswith(project_root + os.sep):
        raise ValueError(f'Local spec path must be within the project directory: {local_path}')
    if not os.path.isfile(real):
        raise ValueError(f'Local spec path does not exist or is not a file: {local_path}')
    if not real.endswith('.json'):
        raise ValueError(f'Local spec path must be a .json file: {local_path}')
    return real


# Specs to fetch: (env var for local override, spec name, output subdir)
SPECS = [
    {
        'name': __validate_spec_name(os.environ.get('SPEC_NAME', 'checkpoint-ai-security')),
        'local_path_env': 'LOCAL_GENERATED_API_PATH',
        'output_dir': 'main',
    },
    {
        'name': __validate_spec_name(os.environ.get('BROWSE_SPEC_NAME', 'checkpoint-browse-security')),
        'local_path_env': 'LOCAL_BROWSE_SPEC_PATH',
        'output_dir': 'browse',
    },
]


def __mkdir_recursive(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def __deposit_file(path, filename, content):
    with open(os.path.join(path, filename), 'w') as f:
        f.write(content)


def __download_spec(spec_name):
    print(f'[fetch-api] Fetching spec "{spec_name}" from SwaggerHub...')
    res = requests.get(f'https://api.swaggerhub.com/apis/{API_SPEC_OWNER}/{spec_name}', headers=swagger_headers, timeout=30)
    all_specs = res.json()
    latest = all_specs['apis'][-1]
    url = next((p['url'] for p in latest['properties'] if p['type'] == 'Swagger'), None)
    if not url:
        raise ValueError(f'No Swagger URL found for spec "{spec_name}"')
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.hostname != 'api.swaggerhub.com':
        raise ValueError(f'Unexpected spec URL origin: {url}')
    print(f'[fetch-api] Downloading from: {url}')
    spec_res = requests.get(url, headers=swagger_headers, timeout=30)
    return spec_res.json()


def fetch_api_specs():
    __mkdir_recursive(OUTPUT_BASE_PATH)

    for spec_cfg in SPECS:
        spec_name = spec_cfg['name']
        out_dir = os.path.join(OUTPUT_BASE_PATH, spec_cfg['output_dir'])
        __mkdir_recursive(out_dir)

        local_path = os.environ.get(spec_cfg['local_path_env'])

        print(f'[fetch-api] Processing spec: {spec_name}')
        if local_path:
            local_path = __validate_local_path(local_path)
            print(f'[fetch-api] Using local spec from: {local_path}')
            shutil.copy(local_path, os.path.join(out_dir, SWAGGER_CONF))
        else:
            spec = __download_spec(spec_name)
            __deposit_file(out_dir, SWAGGER_CONF, json.dumps(spec))

        __deposit_file(out_dir, 'spec', spec_name)
        print(f'[fetch-api] Spec "{spec_name}" ready.')
