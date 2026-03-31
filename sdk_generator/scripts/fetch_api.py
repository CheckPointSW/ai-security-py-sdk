import os
import json
import shutil
import requests

API_SPEC_OWNER = 'Check-Point'
SPEC_NAME = os.environ.get('SPEC_NAME', 'checkpoint-ai-security')
LOCAL_SPEC_PATH = os.environ.get('LOCAL_GENERATED_API_PATH')
SWAGGERHUB_API_KEY = os.environ.get('SWAGGERHUB_API_KEY')

BRANCH_NAME = os.environ.get('CI_COMMIT_REF_NAME') or os.environ.get('BRANCH_NAME')
print(f'[fetch-api] Branch: {BRANCH_NAME}, Build: {os.environ.get("BUILD_JOB_ID")}')
print(f'[fetch-api] Using spec: {SPEC_NAME}')

swagger_headers = {'Content-Type': 'application/json'}
if SWAGGERHUB_API_KEY:
    swagger_headers['Authorization'] = f'Bearer {SWAGGERHUB_API_KEY}'

OUTPUT_BASE_PATH = 'resources/specs'
SWAGGER_CONF = 'swagger.json'


def __mkdir_recursive(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def __deposit_file(path, filename, content):
    with open(os.path.join(path, filename), 'w') as f:
        f.write(content)


def __download_spec():
    print('[fetch-api] Fetching spec from SwaggerHub...')
    res = requests.get(f'https://api.swaggerhub.com/apis/{API_SPEC_OWNER}/{SPEC_NAME}', headers=swagger_headers)
    all_specs = res.json()
    latest = all_specs['apis'][-1]
    url = next((p['url'] for p in latest['properties'] if p['type'] == 'Swagger'), None)
    print(f'[fetch-api] Downloading from: {url}')
    spec_res = requests.get(url, headers=swagger_headers)
    return spec_res.json()


def fetch_api_specs():
    __mkdir_recursive(OUTPUT_BASE_PATH)
    out_dir = os.path.join(OUTPUT_BASE_PATH, 'main')
    __mkdir_recursive(out_dir)

    if LOCAL_SPEC_PATH:
        print(f'[fetch-api] Using local spec from: {LOCAL_SPEC_PATH}')
        shutil.copy(LOCAL_SPEC_PATH, os.path.join(out_dir, SWAGGER_CONF))
    else:
        spec = __download_spec()
        __deposit_file(out_dir, SWAGGER_CONF, json.dumps(spec))

    __deposit_file(out_dir, 'spec', SPEC_NAME)
    print('[fetch-api] Spec ready.')
