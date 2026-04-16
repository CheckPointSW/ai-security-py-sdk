import os
import sys
from pathlib import Path
import subprocess
import shutil
from scripts.fetch_api import fetch_api_specs
from scripts.normalize_spec import normalize_spec
from scripts.post_build import post_build_process

if os.path.exists('../.env'):
    from dotenv import load_dotenv
    load_dotenv()

# (spec subdir, generated package name, generated output path)
PRODUCTS = [
    # ── Sync (urllib3) ──
    {
        'spec_dir': 'main',
        'package_name': 'chkp_ai_security_sdk.generated',
        'generated_rel': 'chkp_ai_security_sdk/generated',
    },
    {
        'spec_dir': 'browse',
        'package_name': 'chkp_ai_security_sdk.generated_browse',
        'generated_rel': 'chkp_ai_security_sdk/generated_browse',
    },
    # ── Async (aiohttp) ──
    {
        'spec_dir': 'main',
        'package_name': 'chkp_ai_security_sdk.generated_async',
        'generated_rel': 'chkp_ai_security_sdk/generated_async',
        'library': 'asyncio',
    },
    {
        'spec_dir': 'browse',
        'package_name': 'chkp_ai_security_sdk.generated_browse_async',
        'generated_rel': 'chkp_ai_security_sdk/generated_browse_async',
        'library': 'asyncio',
    },
]


def generate(product: dict):
    log_prefix = f'[generate:{product["spec_dir"]}]'
    this_dir_path = os.path.dirname(__file__)
    project_dir = Path(this_dir_path, '../')
    specs_path = os.path.join(project_dir, 'resources', 'specs', product['spec_dir'], 'swagger.json')
    generator_path = os.path.join(this_dir_path, 'open_api_tool', 'openapi-generator-cli-7.12.0.jar')
    jre_path = shutil.which('java')
    if not jre_path:
        raise RuntimeError('Java runtime not found. Install Java or ensure java is on PATH.')
    generated_path = os.path.join(project_dir, product['generated_rel'])

    library = product.get('library', '')
    library_prop = f',library={library}' if library else ''
    template_dir = os.path.join(project_dir, 'resources', 'templates', 'python')

    try:
        if os.path.exists(generated_path):
            shutil.rmtree(
                generated_path,
                ignore_errors=True,
                onerror=lambda err: print(f'{log_prefix} Error cleaning generated dir: {err}'),
            )

        cmd = [
            jre_path, '-jar', str(generator_path), 'generate',
            '--generator-name', 'python',
            '--input-spec', str(specs_path),
            '--output', str(project_dir),
            '--template-dir', str(template_dir),
            '--global-property', 'modelDocs=false,modelTests=false',
            '--additional-properties', f'generateSourceCodeOnly=true,packageName={product["package_name"]}{library_prop}',
            '--skip-validate-spec',
        ]
        print(f'{log_prefix} Invoking generator:\n{" ".join(cmd)}')
        subprocess.run(cmd, check=True, stdout=sys.stdout)

    except subprocess.CalledProcessError as e:
        print(f'{log_prefix} Generator error:\n\t{e}')
        raise


def start_generate_process():
    this_dir_path = os.path.dirname(__file__)
    project_dir = Path(this_dir_path, '../')

    # Step 1: Fetch all specs
    fetch_api_specs()

    for product in PRODUCTS:
        spec_dir = product['spec_dir']
        # Copy spec files from CWD-relative path to project root if needed
        cwd_spec_dir = os.path.join('resources', 'specs', spec_dir)
        dest_spec_dir = os.path.join(project_dir, 'resources', 'specs', spec_dir)
        if os.path.exists(cwd_spec_dir) and os.path.abspath(cwd_spec_dir) != os.path.abspath(str(dest_spec_dir)):
            os.makedirs(str(dest_spec_dir), exist_ok=True)
            for fname in os.listdir(cwd_spec_dir):
                shutil.copy2(os.path.join(cwd_spec_dir, fname), os.path.join(str(dest_spec_dir), fname))

        spec_path = os.path.join(project_dir, 'resources', 'specs', spec_dir, 'swagger.json')
        normalize_spec(spec_path)
        generate(product)

    # Step 3: Post-build for both products
    post_build_process()


start_generate_process()
