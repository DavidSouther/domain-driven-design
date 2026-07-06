# Type states: TypeScript reference

### Discriminated union: Rome's bug made unrepresentable

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

### Type state: connection lifecycle with phantom types

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

### Protocols: scope which operations a caller may perform

```typescript
interface Readable { read(): Buffer; }
interface Writable { write(data: Buffer): void; }

function processInput(src: Readable) { /* cannot accidentally call write */ }
function persist(dest: Writable)     { /* cannot accidentally call read  */ }
```
