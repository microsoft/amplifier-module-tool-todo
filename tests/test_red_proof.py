"""DELIBERATE FAILURE -- scratch branch only, never merged.

Exists to prove the Tests job actually executes this repo's suite and can
report a genuine test failure. The job log must read "10 passed, 1 failed":
the passing count is the load-bearing part -- a setup or import error would
show 0 passed and prove nothing.
"""


def test_red_proof_deliberate_failure():
    assert 1 == 2, "deliberate failure to prove the CI test job can go red"
