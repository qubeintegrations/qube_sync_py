"""``python -m qubesync workflows [--drafts] [--check] [--output PATH]``: the ``qubesync``
command (qubesync.workflow_types)."""

import sys

from .workflow_types._cli import main

if __name__ == "__main__":
    sys.exit(main())
