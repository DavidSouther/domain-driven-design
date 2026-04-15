# Type States — Code Reference

Code examples for the `patterns:type-states` skill. Referenced by `patterns/skills/type-states/SKILL.md`.

---

## TypeScript

### Discriminated Union — Rome's bug made unrepresentable

```typescript
// Before: flat interface allows Peace + Dictator (the bug)
interface Rome { ruler: Ruler; status: Status; }

// After: each valid combination is its own type
interface RomeAtPeace { status: "peace"; ruler: "consuls"; }
interface RomeAtWar   { status: "war";   ruler: "dictator"; }

type Rome = RomeAtPeace | RomeAtWar;

// Compiler error — { status: "peace", ruler: "dictator" } is not assignable to Rome
const invalid: Rome = { status: "peace", ruler: "dictator" }; // TS error
```

### Type State — connection lifecycle with phantom types

```typescript
declare const _tag: unique symbol;
class Connection<S> { [_tag]!: S; private constructor() {} }

class Closed {}
class Open   { constructor(readonly socket: Socket) {} }

function open(conn: Connection<Closed>): Connection<Open>   { /* ... */ return conn as any; }
function send(conn: Connection<Open>, data: string): void   { /* ... */ }
function close(conn: Connection<Open>): Connection<Closed>  { /* ... */ return conn as any; }

// Type error — Connection<Closed> is not assignable to Connection<Open>
const c = new Connection<Closed>();
send(c, "hello"); // TS2345
```

### Protocols — scope which operations a caller may perform

```typescript
interface Readable { read(): Buffer; }
interface Writable { write(data: Buffer): void; }

function processInput(src: Readable) { /* cannot accidentally call write */ }
function persist(dest: Writable)     { /* cannot accidentally call read  */ }
```

---

## Python

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

---

## Rust

Rust enforces type states at compile time through ownership and the borrow checker. Consuming the old state on transition is not convention — it is enforced by move semantics.

### Discriminated Union (enum)

```rust
struct Consuls;
struct Dictator;

/// Each variant carries only the fields valid for that state.
enum Rome {
    AtPeace { ruler: Consuls },
    AtWar { ruler: Dictator },
}

fn describe(rome: &Rome) -> &'static str {
    match rome {
        Rome::AtPeace { .. } => "The consuls govern in peacetime.",
        Rome::AtWar { .. }   => "The dictator leads in wartime.",
    }
}

// The compiler exhaustively checks every variant — no invalid combination possible.
```

### Type State — zero-cost phantom types

```rust
use std::marker::PhantomData;

struct Closed;
struct Open;

/// The state parameter S is erased at runtime — zero overhead.
struct Connection<S> {
    _state: PhantomData<S>,
}

impl Connection<Closed> {
    pub fn new() -> Self {
        Connection { _state: PhantomData }
    }

    /// Consumes the Closed connection; caller cannot use it again.
    pub fn open(self) -> Connection<Open> {
        Connection { _state: PhantomData }
    }
}

impl Connection<Open> {
    pub fn send(&self, data: &str) {
        let _ = data; // send over socket...
    }

    /// Consumes the Open connection; caller cannot use it again.
    pub fn close(self) -> Connection<Closed> {
        Connection { _state: PhantomData }
    }
}

fn demo() {
    let conn = Connection::<Closed>::new();
    // conn.send("hello");  // compile error: no method `send` on Connection<Closed>
    let conn = conn.open();
    conn.send("hello");
    let _closed = conn.close();
    // conn.send("world"); // compile error: value moved
}
```

### Protocols — trait-based capability scoping

```rust
pub trait Readable {
    fn read(&self) -> Vec<u8>;
}

pub trait Writable {
    fn write(&self, data: &[u8]);
}

fn process_input(src: &dyn Readable) {
    let _ = src.read(); // cannot accidentally call write
}

fn persist(dest: &dyn Writable) {
    dest.write(b"data"); // cannot accidentally call read
}
```
