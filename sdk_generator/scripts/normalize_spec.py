"""Normalize OpenAPI 3.1.0 spec to 3.0.3 for generator compatibility.

Converts anyOf nullable patterns:
    {"anyOf": [{"type": "string"}, {"type": "null"}]}
to:
    {"type": "string", "nullable": true}
"""
import json
import os


def _normalize_schema(obj):
    """Recursively normalize a schema object."""
    if not isinstance(obj, dict):
        return obj

    # Convert anyOf nullable: [{"type": X, ...}, {"type": "null"}] -> {"type": X, ..., "nullable": true}
    if 'anyOf' in obj and isinstance(obj['anyOf'], list):
        non_null = [s for s in obj['anyOf'] if not (isinstance(s, dict) and s.get('type') == 'null')]
        has_null = any(isinstance(s, dict) and s.get('type') == 'null' for s in obj['anyOf'])
        if has_null and len(non_null) == 1:
            merged = {k: v for k, v in obj.items() if k != 'anyOf'}
            merged.update(non_null[0])
            merged['nullable'] = True
            return _normalize_schema(merged)

    result = {}
    for key, value in obj.items():
        if isinstance(value, dict):
            result[key] = _normalize_schema(value)
        elif isinstance(value, list):
            result[key] = [_normalize_schema(item) if isinstance(item, (dict, list)) else item for item in value]
        else:
            result[key] = value
    return result


def normalize_spec(spec_path: str):
    """Normalize an OpenAPI 3.1.x spec file to 3.0.3 in-place."""
    if not os.path.exists(spec_path):
        print(f'[normalize] Spec not found at {spec_path}, skipping')
        return

    with open(spec_path, 'r') as f:
        spec = json.load(f)

    original_version = spec.get('openapi', '')
    if not original_version.startswith('3.1'):
        print(f'[normalize] Spec is already {original_version}, no conversion needed')
        return

    spec['openapi'] = '3.0.3'
    spec = _normalize_schema(spec)

    with open(spec_path, 'w') as f:
        json.dump(spec, f, indent=2)

    print(f'[normalize] Converted spec from {original_version} to 3.0.3')
