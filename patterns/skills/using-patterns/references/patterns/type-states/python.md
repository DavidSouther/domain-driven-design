# Type States — Python Reference

Python's type system is structural and checked by tools like mypy. Discriminated unions use `Literal` types; type states use `Generic` with phantom types enforced by mypy, not the runtime.

### Discriminated Union

```python
from dataclasses import dataclass
from typing import Literal, Union

@dataclass
class RomeAtPeace:
    status: Literal["peace"] = "peace"
    ruler: Literal["consuls"] = "consuls"

@dataclass
class RomeAtWar:
    status: Literal["war"] = "war"
    ruler: Literal["dictator"] = "dictator"

Rome = Union[RomeAtPeace, RomeAtWar]

def describe(rome: Rome) -> str:
    match rome:
        case RomeAtPeace():
            return "The consuls govern in peacetime."
        case RomeAtWar():
            return "The dictator leads in wartime."
```

### Type State — phantom generic

```python
from typing import Generic, TypeVar

class Closed: ...
class Open: ...

S = TypeVar("S")

class Connection(Generic[S]):
    """State S is a phantom type — it exists only in type annotations."""
    def __init__(self) -> None:
        self._socket: object | None = None

def open_conn(conn: "Connection[Closed]") -> "Connection[Open]":
    result: Connection[Open] = Connection()
    # set up socket...
    return result

def send(conn: "Connection[Open]", data: str) -> None:
    ...  # mypy ensures only Open connections reach here

def close_conn(conn: "Connection[Open]") -> "Connection[Closed]":
    result: Connection[Closed] = Connection()
    return result
```

### Protocols — structural capability scoping

```python
from typing import Protocol

class Readable(Protocol):
    def read(self) -> bytes: ...

class Writable(Protocol):
    def write(self, data: bytes) -> None: ...

def process_input(src: Readable) -> None:
    data = src.read()  # cannot accidentally call write

def persist(dest: Writable) -> None:
    dest.write(b"data")  # cannot accidentally call read
```
