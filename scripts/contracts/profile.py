"""Shared input contract. Structural validity does not certify candidate facts."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / 'src/knowledge/resume-schema.json').read_text(encoding='utf-8'))

class ContractError(ValueError):
    pass


def _normalize(value, schema, path):
    types = schema.get('type', [])
    types = [types] if isinstance(types, str) else types
    if value is None:
        if 'null' not in types:
            raise ContractError(path + ': null is not allowed')
        return [] if 'array' in types else {} if 'object' in types else None
    if isinstance(value, str):
        if 'string' not in types:
            raise ContractError(path + ': expected ' + '/'.join(types))
        value = value.strip() or None
        if value is not None and 'enum' in schema and value not in schema['enum']:
            raise ContractError(path + ': invalid value')
        return value
    if isinstance(value, dict) and 'object' in types:
        properties = schema.get('properties', {})
        unknown = set(value) - set(properties)
        if unknown:
            raise ContractError(path + ': unsupported fields: ' + ', '.join(sorted(unknown)))
        result = {}
        for key, child in properties.items():
            if key in value:
                item = _normalize(value[key], child, path + '.' + key)
                if item is not None and item != {} and item != []:
                    result[key] = item
        return result
    if isinstance(value, list) and 'array' in types:
        values = [_normalize(item, schema['items'], path + '[' + str(i) + ']') for i, item in enumerate(value)]
        return [item for item in values if item is not None and item != '' and item != {}]
    raise ContractError(path + ': expected ' + '/'.join(types))


def normalize_profile(raw):
    result = _normalize(raw, SCHEMA, 'profile')
    result.setdefault('basics', {})
    for field in ('skills', 'experience', 'projects', 'education', 'certifications'):
        result.setdefault(field, [])
    return result


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def missing_fields(profile):
    # Informational gaps; optional omissions never turn into invented defaults.
    return ['basics.' + field for field in ('name', 'title', 'email', 'phone')
            if not profile.get('basics', {}).get(field)]


def delivery_errors(profile):
    errors = []
    if not profile['basics'].get('name'):
        errors.append('A non-empty candidate name is required for delivery')
    if not any(profile.get(key) for key in ('experience', 'projects', 'education', 'skills', 'certifications')):
        errors.append('At least one substantive resume section is required for delivery')
    return errors


def document(kind, profile, source=None):
    if kind not in ('draft', 'master', 'variant'):
        raise ContractError('Unknown document kind: ' + str(kind))
    profile = normalize_profile(profile)
    return {'schemaVersion': '1.0', 'kind': kind, 'profile': profile,
            'profileSha256': digest(profile), 'missingFields': missing_fields(profile),
            'source': copy.deepcopy(source or {})}


def load_document(raw):
    if not isinstance(raw, dict):
        raise ContractError('Profile document must be an object')
    if 'profile' not in raw:
        # Existing --profile-json inputs are explicit user/Agent supplied facts.
        return document('master', raw, {'type': 'legacy-user-input'})
    unknown = set(raw) - {'schemaVersion', 'kind', 'profile', 'profileSha256', 'missingFields', 'source'}
    if unknown:
        raise ContractError('Unsupported document fields: ' + ', '.join(sorted(unknown)))
    if raw.get('schemaVersion') != '1.0':
        raise ContractError('Unsupported profile schemaVersion')
    source = raw.get('source', {})
    if not isinstance(source, dict):
        raise ContractError('Document source must be an object')
    result = document(raw.get('kind'), raw['profile'], source)
    if raw.get('profileSha256') and result['profileSha256'] != raw['profileSha256']:
        raise ContractError('Profile hash mismatch; regenerate metadata after editing facts')
    if result['kind'] == 'variant' and not source.get('masterSha256'):
        raise ContractError('Variant requires source.masterSha256')
    return result
