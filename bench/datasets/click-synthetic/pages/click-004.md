# Pin help wrapping at the invocation boundary

Synthetic benchmark memory, not an upstream maintainer policy.

## Origin

`page_origin`: `other_session`

Fictional earlier correction from a different synthetic session about deterministic help tests; not the target correction.

## Scope

Exact help-wrapping regression tests for a requested terminal width; not general terminal discovery or production layout changes.

## Convention points

1. Pass terminal_width=48 explicitly to CliRunner.invoke for the help request.
2. Do not rely on the host terminal size or a COLUMNS environment mutation for this exact-width test.
3. Assert successful exit and the expected wrapping for that width without changing production help formatting to make the test pass.

## Practice

Request help with runner.invoke(cli, ["--help"], terminal_width=48). Keep the expected wrapped output local to the test. Do not depend on the running shell or rewrite production text to conceal a width-dependent test.

## Public API references

- [Click 8.1.8 testing guide](https://github.com/pallets/click/blob/934813e4d421/docs/testing.rst)
- [Click testing tests](https://github.com/pallets/click/blob/934813e4d421/tests/test_testing.py)
