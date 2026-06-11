"""CLI entrypoint for the eval/red-team suite (CI release gate). `python -m condominioos.evals.run_suite`."""

from __future__ import annotations

import sys

from condominioos.evals.suite import run_suite


def main() -> int:
    passed, total, failures = run_suite()
    print(f"Firewall red-team suite: {passed}/{total} passed")
    for f in failures:
        print(f"  FAIL: {f}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
