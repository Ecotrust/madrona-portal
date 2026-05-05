# Configuration Standard

This project uses a layered configuration model with strict precedence and typed parsing.

## Precedence

For runtime settings, use this priority order:

1. Environment variable
2. config.ini value
3. Safe default in code

This keeps deployments flexible while preserving stable local defaults.

## Required Standard

Use typed helper functions from marco.config_helpers for app settings.

- env_str for string settings
- env_bool for boolean settings
- env_int for integer settings

Do not parse booleans ad hoc in settings code.

## Why This Standard Exists

- Avoid inconsistent precedence across settings
- Prevent string-typed booleans from silently behaving incorrectly
- Make behavior testable and explicit

## Approved Patterns

Use typed helper access for standard settings:

- DEBUG
- EMAIL_USE_TLS
- EMAIL_PORT
- SECRET_KEY and other credentials
- STATIC and MEDIA path settings

Direct environment lookups are still acceptable for special alias chains where multiple environment variable names must be supported for compatibility, such as DB_* and SQL_* overrides.

## Test Coverage

The helper contract is enforced by tests in marco/marco/tests/test_config_helpers.py:

- env over config precedence
- config over default fallback
- strict boolean parsing and invalid-value failures
- integer parsing behavior
