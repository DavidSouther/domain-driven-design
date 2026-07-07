# Using feature flags in Python

One toggle point reads the injected `Flags` port and branches. The default branch is today's behavior. The targeting stays in the provider behind the port. The test exercises both branches.

```python
# checkout.py: one toggle point, at the edge of the new path
from flags import Flags, FlagContext  # installed by configuring-feature-flags


def checkout(flags: Flags, ctx: FlagContext, cart: Cart) -> Receipt:
    if flags.enabled("release.checkout.new-flow", False, ctx):
        return new_checkout(cart)
    return current_checkout(cart)  # the default branch is today's behavior
```

```python
# test_checkout.py: both states ship, so both states are tested
from checkout import checkout
from flags import FlagContext


class FakeFlags:
    def __init__(self, on: bool) -> None:
        self._on = on

    def enabled(self, key: str, default: bool, ctx: FlagContext) -> bool:
        return self._on


CTX = FlagContext(environment="test")


def test_flag_off_runs_the_current_flow() -> None:
    assert checkout(FakeFlags(on=False), CTX, cart).via == "current"


def test_flag_on_runs_the_new_flow() -> None:
    assert checkout(FakeFlags(on=True), CTX, cart).via == "new"
```

When the new flow is fully rolled out, delete the flag, the `if`, and `current_checkout`, leaving `checkout` as a direct call.
