# Feed ordinary prompt input through the runner and test the emulated echo

Synthetic benchmark memory, not an upstream maintainer policy.

## Origin

`page_origin`: `same_session`

Same-session exposure control: this page is synthesized only from the initial rule reminder already visible in this case prefix, before the task and before the held-out correction. No future correction is used. Both arms already have that reminder; this is not clean other-session transfer evidence.

## Scope

Non-hidden Click prompt regression tests in this synthetic session; hidden-password prompts are excluded.

## Convention points

1. Supply a newline-terminated answer through CliRunner.invoke(input=...) and execute the real prompt path rather than patching input or bypassing the command.
2. Assert that captured output contains the ordinary prompt and its emulated echo of the supplied answer.
3. Assert the resulting greeting and successful exit status, not only the prompt echo.

## Practice

Pass the answer with a trailing newline to runner.invoke. Ordinary, non-hidden prompt output includes the prompt and echoed answer. Check those alongside the greeting and exit_code. Do not mock builtins.input or call the callback in place of the prompt path.

## Public API references

- [Click 8.1.8 testing guide](https://github.com/pallets/click/blob/934813e4d421/docs/testing.rst)
- [Click testing tests](https://github.com/pallets/click/blob/934813e4d421/tests/test_testing.py)
