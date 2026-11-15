# Keep file-command test setup and invocation inside filesystem isolation

Synthetic benchmark memory, not an upstream maintainer policy.

## Origin

`page_origin`: `other_session`

Fictional earlier correction in a different synthetic session. It does not quote or summarize this target session or its held-out correction.

## Scope

Regression tests for Click commands that consume relative files; not production command implementation or unrelated unit tests.

## Convention points

1. Create the input fixture and invoke the file-consuming command inside the same CliRunner.isolated_filesystem context.
2. Exercise the command with CliRunner.invoke rather than directly calling its callback or cli.main.
3. Assert both successful exit status and the expected captured file content in the result.

## Practice

Put fixture creation and runner.invoke(cat, ["sample.txt"]) in one runner.isolated_filesystem() block. Check result.exit_code and result.output; do not write test fixtures to the repository root.

## Public API references

- [Click 8.1.8 testing guide](https://github.com/pallets/click/blob/934813e4d421/docs/testing.rst)
- [Click testing tests](https://github.com/pallets/click/blob/934813e4d421/tests/test_testing.py)
