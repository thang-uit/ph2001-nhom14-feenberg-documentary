#!/usr/bin/env python3
"""Compatibility guard for the retired V11 R5 cleanup command.

The active delivery is V11 R6.  This guard intentionally refuses to delete
anything so an old command cannot remove R6 assets or the R5 rollback.
Use ``cleanup_latest_v11_r6.py`` and review its dry-run first.
"""

from __future__ import annotations

raise SystemExit(
    "V11 R5 cleanup is retired; no files were changed. "
    "Use scripts/cleanup_latest_v11_r6.py (dry-run is the default)."
)
