# Do not concurrently invoke CliRunner in threads in one interpreter

Synthetic benchmark memory, not an upstream maintainer policy.

## Origin

`page_origin`: `other_session`

Fictional independent earlier correction in another synthetic session, inspired by the public thread-safety warning. No real session is copied.

## Scope

A helper running several Click command invocations in the same Python interpreter; not an asserted ban on independent process-based test workers.

## Convention points

1. Run these CliRunner invocations sequentially rather than concurrently in threads within one interpreter, because runner isolation changes interpreter-global state.
2. Keep each invocation result separate and assert its own expected output instead of relying on interleaved shared capture.

## Practice

Use a straightforward sequential loop or sequential parameter cases, keep each Result local, and check the corresponding greeting. CliRunner testing helpers change interpreter-wide state and are not thread-safe. This does not claim separate processes can never run tests concurrently.

## Public API references

- [Click 8.1.8 testing guide](https://github.com/pallets/click/blob/934813e4d421/docs/testing.rst)
- [Click testing tests](https://github.com/pallets/click/blob/934813e4d421/tests/test_testing.py)
