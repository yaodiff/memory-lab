# Cover root-group setup when testing a subcommand

Synthetic benchmark memory, not an upstream maintainer policy.

## Origin

`page_origin`: `other_session`

Fictional earlier correction in a different synthetic session. No evidence is taken from this target session.

## Scope

Integration-style tests for a Click group whose --debug root option affects its sync subcommand; not isolated callback unit tests.

## Convention points

1. Invoke the root cli group with CliRunner.invoke and an explicit sync subcommand token, rather than calling sync or sync.callback directly.
2. Put the root --debug option before the sync token so the root context handles it.
3. Assert successful exit and both the root debug message and subcommand sync message in captured output.

## Practice

Use runner.invoke(cli, ["--debug", "sync"]). Exercise the group callback and option parsing, then verify exit_code and both messages. Do not turn an integration-style group test into a direct subcommand callback test.

## Public API references

- [Click 8.1.8 testing guide](https://github.com/pallets/click/blob/934813e4d421/docs/testing.rst)
- [Click testing tests](https://github.com/pallets/click/blob/934813e4d421/tests/test_testing.py)
