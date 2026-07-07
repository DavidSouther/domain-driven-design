# Configuring feature flags in Python

The composition root builds one evaluation client behind a vendor-neutral port and injects it. Call sites receive the port, never a vendor SDK.

```python
# flags.py: the vendor-neutral port every call site reads through
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class FlagContext:
    environment: str
    user_id: str | None = None


class Flags(Protocol):
    def enabled(self, key: str, default: bool, ctx: FlagContext) -> bool: ...
```

```python
# fail_safe.py: an unreachable backing resolves to the default (current behavior)
class FailSafeFlags:
    def __init__(self, inner: Flags) -> None:
        self._inner = inner

    def enabled(self, key: str, default: bool, ctx: FlagContext) -> bool:
        try:
            return self._inner.enabled(key, default, ctx)
        except Exception:
            return default
```

```python
# static_flags.py: a fully runnable backing for local and CI
class StaticFlags:
    def __init__(self, values: dict[str, bool] | None = None) -> None:
        self._values = values or {}

    def enabled(self, key: str, default: bool, ctx: FlagContext) -> bool:
        return self._values.get(key, default)
```

```python
# bootstrap.py: built once at the composition root, then injected
def build_flags(environment: str) -> Flags:
    # Production backs the port with a vendor SDK that evaluates a locally cached
    # ruleset (LaunchDarkly, Unleash), or with an OpenFeature client, whose
    # synchronous evaluation is client.get_boolean_value(key, default, ctx).
    overrides = {"release.checkout.new-flow": True} if environment == "local" else {}
    return FailSafeFlags(StaticFlags(overrides))
```

The flag inventory (key, owner, expiry) lives beside this module, and a CI check fails any flag past its expiry.
