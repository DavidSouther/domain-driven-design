"""Promptfoo provider entry point for the invocation-phases pilot."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any, Mapping

MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

from service import call_api as _call_api


def call_api(
    prompt: str,
    options: Mapping[str, Any],
    context: Mapping[str, Any],
) -> Mapping[str, Any]:
    return _call_api(prompt, options, context)
