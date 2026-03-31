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


def generate(spec: str = 'main'):
    log_prefix = '[generate]'
    this_dir_path = os.path.dirname(__file__)
    project_dir = Path(this_dir_path, '../')
    specs_path = os.path.join(project_dir, 'resources', 'specs', spec, 'swagger.json')
    generator_path = os.path.join(this_dir_path, 'open_api_tool', 'openapi-generator-cli-7.12.0.jar')
    jre_path = os.getenv('JRE_PATH', 'java')
    generated_path = os.path.join(project_dir, 'chkp_ai_security_sdk', 'generated')

    try:
        if os.path.exists(generated_path):
            shutil.rmtree(
                generated_path,
                ignore_errors=True,
                onerror=lambda err: print(f'[generate] Error cleaning generated dir: {err}'),
            )

        cmd_line = (
            f'"{jre_path}" -jar {generator_path} generate'
            f' --generator-name python'
            f' --input-spec {specs_path}'
            f' --output {project_dir}'
            f' --global-property modelDocs=false,modelTests=false'
            f' --additional-properties=generateSourceCodeOnly=true,packageName=chkp_ai_security_sdk.generated'
            f' --skip-validate-spec'
        )
        print(f'{log_prefix} Invoking generator:\n{cmd_line}')
        subprocess.run(cmd_line, shell=True, check=True, stdout=sys.stdout)

    except subprocess.CalledProcessError as e:
        print(f'[generate] Generator error:\n\t{e}')
        raise


def start_generate_process():
    this_dir_path = os.path.dirname(__file__)
    project_dir = Path(this_dir_path, '../')
    spec_path = os.path.join(project_dir, 'resources', 'specs', 'main', 'swagger.json')
    fetch_api_specs()
    # Copy spec files from CWD-relative path to project root if needed
    cwd_spec_dir = os.path.join('resources', 'specs', 'main')
    dest_spec_dir = os.path.join(project_dir, 'resources', 'specs', 'main')
    if os.path.exists(cwd_spec_dir) and os.path.abspath(cwd_spec_dir) != os.path.abspath(str(dest_spec_dir)):
        os.makedirs(str(dest_spec_dir), exist_ok=True)
        for fname in os.listdir(cwd_spec_dir):
            shutil.copy2(os.path.join(cwd_spec_dir, fname), os.path.join(str(dest_spec_dir), fname))
    normalize_spec(spec_path)
    generate()
    post_build_process()


start_generate_process()
