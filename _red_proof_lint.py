"""DELIBERATE LINT DEFECT -- scratch branch only, never merged.

`os` is imported and never used: ruff F401, inside the pinned E4,E7,E9,F set.
Proves the Lint job fails for its own reason, independently of the tests.
Not collected by pytest (testpaths = ["tests"]).
"""

import os
