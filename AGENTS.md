# Verification Rules

1. All code changes must be accompanied by relevant tests.
2. Ensure there are no code paths that execute automatic deletion of source files.
3. Verify that the task status is consistent with `MigrationStatus` enum.
4. Pass all test cases using `pytest`.
