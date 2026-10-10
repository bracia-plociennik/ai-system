"""Resolve approved local root expressions without shell evaluation or filesystem writes."""
from __future__ import annotations

import os
from pathlib import Path
import re


class LocalPathError(ValueError):
    """A path cannot be interpreted within the selected local context."""


VARIABLE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")
ALLOWED = {"HOME", "AI_SYSTEM_HOME", "AI_SYSTEM_WORKSPACE_HOME"}


def resolve_path(value, *, workspace=None, base=None, allow_relative=False, environment=None):
    """Return an absolute lexical path, rejecting links before normalization.

    Explicit workspace wins over the environment. Caller-supplied bases are
    mandatory for relative compatibility; no implicit CWD/workspace discovery.
    Missing paths are returned as missing, for the caller's readiness policy.
    """
    try:
        raw = os.fspath(value)
    except TypeError:
        raise LocalPathError("invalid-path-value") from None
    if not isinstance(raw, str) or not raw or any(ord(c) < 32 for c in raw):
        raise LocalPathError("invalid-path-value")
    env = dict(os.environ if environment is None else environment)
    roots = {"HOME": env.get("HOME", str(Path.home())),
             "AI_SYSTEM_HOME": env.get("AI_SYSTEM_HOME", str(Path(__file__).resolve().parents[2])),
             "AI_SYSTEM_WORKSPACE_HOME": os.fspath(workspace) if workspace is not None
             else env.get("AI_SYSTEM_WORKSPACE_HOME")}

    def root(name):
        if name not in ALLOWED:
            raise LocalPathError("unknown-path-variable")
        text = roots[name]
        if not isinstance(text, str) or not text or not Path(text).is_absolute():
            raise LocalPathError("missing-or-relative-path-context")
        if "$" in text or "~" in text or any(ord(c) < 32 for c in text):
            raise LocalPathError("recursive-or-invalid-path-context")
        return text

    if raw == "~" or raw.startswith("~/"):
        raw = root("HOME") + raw[1:]
    elif raw.startswith("~"):
        raise LocalPathError("foreign-home-expansion")
    raw = VARIABLE.sub(lambda match: root(match.group(1) or match.group(2)), raw)
    if "$" in raw:
        raise LocalPathError("malformed-path-expression")
    candidate = Path(raw)
    if not candidate.is_absolute():
        if not allow_relative or base is None:
            raise LocalPathError("absolute-path-required")
        parent = Path(base)
        if not parent.is_absolute():
            raise LocalPathError("absolute-base-required")
        candidate = parent / candidate
    # resolve() would hide symlink aliases. Check unnormalized components first,
    # including paths containing '..', then normalize lexically without following.
    if any(p.is_symlink() for p in (candidate, *candidate.parents)):
        raise LocalPathError("linked-path-component")
    return Path(os.path.abspath(candidate))
