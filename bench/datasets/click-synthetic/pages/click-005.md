# Preserve ANSI at the runner boundary for a color-specific assertion

Synthetic benchmark memory, not an upstream maintainer policy.

## Origin

`page_origin`: `same_session`

Same-session exposure control: this page summarizes the initial ANSI-test reminder already in the prefix. It uses no future target correction. Its information is already available to both arms, so it must not be pooled with independent other-session pages.

## Scope

Tests specifically asserting Click styled output and ANSI preservation; not ordinary plain-output tests or global color policy.

## Convention points

1. Invoke the styled command with CliRunner.invoke(color=True) so ANSI escapes are preserved for this test.
2. Assert both the expected ANSI styling escape and the semantic output text.
3. Keep production styling behavior unchanged; do not globally force color or alter the command merely to satisfy the test.

## Practice

Use runner.invoke(status, [], color=True), check the expected green ANSI sequence and Ready text, and leave production click.secho unchanged. Do not assert only readable text in a test whose purpose is styling preservation.

## Public API references

- [Click 8.1.8 testing guide](https://github.com/pallets/click/blob/934813e4d421/docs/testing.rst)
- [Click testing tests](https://github.com/pallets/click/blob/934813e4d421/tests/test_testing.py)
