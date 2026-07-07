# Type states, rust reference

Rust enforces type states at compile time through ownership and the borrow checker. Consuming the old state on transition is not convention. Move semantics enforce it.

### Discriminated union (enum)

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

// The compiler exhaustively checks every variant: no invalid combination possible.
```

### Type state, zero-cost phantom types

```rust
use std::marker::PhantomData;

struct Closed;
struct Open;

/// The state parameter S is erased at runtime: zero overhead.
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

### Protocols, trait-based capability scoping

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
