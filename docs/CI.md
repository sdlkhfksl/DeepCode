# Working with CI

CI checks the complete pull request from its merge base, so unrelated changes
added to the target branch do not count as changes in the PR. A README update
inside a PR that also changes runtime code still receives the runtime checks.
A PR containing only README files, `docs/`, or `assets/readme/` skips runtime
tests and builds, while formatting, secret scanning, and dependency review
remain active. Unknown paths and missing comparison history run checks.

The classification lives in `scripts/ci_scope.py`, used through
`.github/actions/ci-scope`. Runtime test jobs keep their existing check names
when their heavy steps are unnecessary, so required checks do not wait for a
workflow that never started. Desktop bundle jobs retain their existing scope.

## What a passing check means

| Check | What it verifies |
|---|---|
| Python 3.12, 3.13, and 3.14 | The full backend suite on Ubuntu 24.04 |
| Windows lifecycle | Real file locks, ACLs, recovery, background service operations, and discovery races |
| Browser | Chromium interactions with the real local service and a deterministic test Agent |
| Python package | Distribution metadata, packaged resources, and installation in a clean environment |
| Desktop quality | Frontend tests, types, protocol consistency, Rust formatting, lint, and tests |
| Four platform bundles | Build artifacts, packaged runtime startup, resources, and platform package checks |
| Security | Secret history, dependency vulnerabilities, and dependency licenses |

Browser CI does not call a paid model. Live-provider, native GUI, and actual
OS login/reboot acceptance remain separate from these regression checks.
Functional startup tests use the launcher's readiness policy. Their timeouts
are test budgets, not published startup-performance guarantees.

## Reproduce the Python test environment

From the repository root, create and activate a Python 3.12, 3.13, or 3.14
virtual environment. Then run:

```sh
python -m pip install -r scripts/ci/requirements.lock
python -m pip install --no-deps --no-build-isolation -e '.[test]'
python -m pip check
python -m pytest -q --durations=10
pre-commit run --all-files
```

The lock contains the package's runtime/test dependencies and CI tools. Runtime
versions shared with Desktop follow `desktop/sidecar-requirements.lock`.
`--no-deps` prevents editable installation from silently adding unlocked runtime
dependencies; `pip check` reports missing or incompatible requirements.

After changing package requirements, test extras, or the sidecar lock, regenerate
the CI lock with `uv` and commit the result:

```sh
uv pip compile scripts/ci/requirements.in --python-version 3.12 --universal --no-emit-package deepcode-hku --output-file scripts/ci/requirements.lock
```

Add `--upgrade` when deliberately refreshing all compatible dependency pins.
Run tests and the security checks after refreshing. The security workflow audits
the CI lock as well as the packaged runtime. Package installation and the live
package dependency audit still resolve supported dependency ranges, so the fixed
test baseline does not replace installation compatibility checks.

## Diagnose a failure

Inspect the earliest failing step. Python and Windows jobs upload JUnit reports
with test names and durations; browser jobs retain failure traces and screenshots.
Packaged startup errors include worker output. A failure while stopping the test
service is attached to the original exception, and temporary cleanup is still
attempted. A cleanup failure on its own also fails the check.

PR updates cancel superseded runs. Rust dependency and pre-commit caches reduce
repeated setup; caches do not substitute for tests or package validation. A cold
cache must produce the same verdict as a warm cache. Failed tests are not
automatically retried until they turn green.
