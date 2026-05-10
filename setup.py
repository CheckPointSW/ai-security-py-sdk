# -*- coding: utf-8 -*-
from pathlib import Path
from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / 'README.md').read_text(encoding='utf-8')

prod_dependencies = [
    'aenum~=3.1',
    'certifi>=2024.0,<2026.0',
    'charset-normalizer~=3.3',
    'frozendict~=2.3',
    'idna~=3.7',
    'MarkupSafe~=2.1',
    'python-dateutil~=2.8',
    'python-dotenv~=1.0',
    'requests~=2.32',
    'pydantic>=2.0',
    'typing-extensions>=4.12',
    'pyjwt~=2.8',
    'unitsnet-py>=0.1.82',
    'urllib3~=2.2',
    'aiohttp~=3.9',
    'aiohttp-retry~=2.8',
]

setup(
    name='chkp-ai-security-sdk',
    version='1.0.0',
    keywords='python, ai, security, sdk, checkpoint, genai, workforce ai, ai security, browse security',
    license='MIT',
    description='Check Point AI Security Official Python SDK (Workforce AI + Browse Security)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Haim Kastner',
    author_email='haimk@checkpoint.com',
    maintainer='Haim Kastner',
    maintainer_email='haimk@checkpoint.com',
    url='https://github.com/CheckPointSW/ai-security-py-sdk',
    packages=find_packages(exclude=['sdk_generator', 'scripts', 'tests']),
    package_data={'': ['*.json']},
    install_requires=prod_dependencies,
    python_requires='>=3.9,<4.0',
)
