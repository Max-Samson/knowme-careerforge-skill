#!/usr/bin/env python3
"""Retired compatibility entry: repository contents are not candidate evidence."""
import json
import sys


def main():
    # Intentionally do not parse repository/output paths or read candidate inputs.
    # Old CLI/npm/direct callers must fail before creating or overwriting files.
    print(json.dumps({
        'status': 'FAIL',
        'stage': 'unsupported',
        'errors': ['Repository-to-resume extraction is not supported. Use user-provided facts with forge --profile-json.'],
        'warnings': [],
        'outputs': {},
    }))
    return 1


if __name__ == '__main__':
    sys.exit(main())
