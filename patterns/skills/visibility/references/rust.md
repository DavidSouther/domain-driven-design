# Visibility — Rust Reference

Rust's module system enforces visibility at compile time. Fields default to private; `pub` is opt-in. Borrowing rules give reference-only getters for free: `&T` cannot mutate, `&mut T` is the only way to mutate, and the compiler decides who has which.

```rust
mod order {
    use std::convert::TryFrom;

    #[derive(Debug, Clone)]
    pub struct OrderLine {
        pub sku: String,
        pub qty: u32,
        pub cents: u64,
    }

    #[derive(Debug, Clone, Copy, PartialEq, Eq)]
    pub enum OrderStatus {
        Open,
        Cancelled,
        Shipped,
    }

    pub struct Order {
        id: OrderId,
        status: OrderStatus,
        lines: Vec<OrderLine>,
        total: u64,
    }

    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub struct OrderId(String);

    impl TryFrom<&str> for OrderId {
        type Error = String;
        fn try_from(raw: &str) -> Result<Self, Self::Error> {
            if raw.is_empty() { return Err("OrderId must be non-empty".into()); }
            Ok(OrderId(raw.to_string()))
        }
    }

    impl Order {
        // Private constructor — outside this module, only `builder` can produce an Order.
        fn new(id: OrderId) -> Self {
            Order { id, status: OrderStatus::Open, lines: Vec::new(), total: 0 }
        }

        pub fn builder(id: OrderId) -> OrderBuilder {
            OrderBuilder { id, lines: Vec::new() }
        }

        // Reference-only getters. Callers cannot mutate through &Order.
        pub fn id(&self) -> &OrderId { &self.id }
        pub fn status(&self) -> OrderStatus { self.status }
        pub fn total(&self) -> u64 { self.total }
        pub fn lines(&self) -> &[OrderLine] { &self.lines }

        // Explicit mutation: requires &mut self and enforces invariants.
        pub fn add_line(&mut self, line: OrderLine) -> Result<(), String> {
            if self.status != OrderStatus::Open {
                return Err("cannot modify a closed order".into());
            }
            self.total += line.cents * line.qty as u64;
            self.lines.push(line);
            Ok(())
        }

        pub fn cancel(&mut self) -> Result<(), String> {
            if self.status == OrderStatus::Shipped {
                return Err("cannot cancel a shipped order".into());
            }
            self.status = OrderStatus::Cancelled;
            Ok(())
        }
    }

    pub struct OrderBuilder {
        id: OrderId,
        lines: Vec<OrderLine>,
    }

    impl OrderBuilder {
        pub fn with_line(mut self, line: OrderLine) -> Self {
            self.lines.push(line);
            self
        }

        pub fn build(self) -> Result<Order, String> {
            if self.lines.is_empty() {
                return Err("order must have at least one line".into());
            }
            let mut order = Order::new(self.id);
            for line in self.lines {
                order.add_line(line)?;
            }
            Ok(order)
        }
    }
}
```

Key details:
- All fields of `Order` are private to the `order` module; outside callers cannot read or write them directly.
- `lines(&self) -> &[OrderLine]` hands out an immutable borrow; `.push` is unavailable through the slice.
- `add_line` and `cancel` require `&mut self`. The borrow checker prevents calling them while another reference is alive.
- `Order::new` is module-private. Outside `mod order`, `Order::builder` is the only construction path.
- `OrderId` uses `TryFrom` to validate at the boundary, composing visibility with `patterns:newtype` and `patterns:parse-dont-validate`.
- For pure value objects, prefer a `pub struct` with `pub` fields *and* no mutation methods; immutability replaces visibility as the protection mechanism.
