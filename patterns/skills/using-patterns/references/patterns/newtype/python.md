# NewType, Python reference

Python lacks compile-time branding, so newtypes use frozen dataclasses. mypy enforces the distinction; the `value` field carries the underlying primitive.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class AccountId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.startswith("acc-"):
            raise ValueError(f"Invalid AccountId: {self.value}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Cents:
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int) or self.value < 0:
            raise ValueError(f"Invalid Cents: {self.value}")


def transfer(from_account: AccountId, to_account: AccountId, amount: Cents) -> None:
    ...


# Type error (mypy) — plain str is not AccountId:
transfer("acc-123", "acc-456", 5000)  # mypy error

# Correct:
transfer(AccountId("acc-123"), AccountId("acc-456"), Cents(5000))
```
