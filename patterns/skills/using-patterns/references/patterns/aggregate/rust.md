# Rust aggregate reference

```rust
pub struct LineItem {
    product_id: String,
    qty: u32,
    unit_price_cents: u64,
}

impl LineItem {
    pub fn new(product_id: &str, qty: u32, unit_price_cents: u64) -> Result<Self, String> {
        if qty == 0 {
            return Err("qty must be positive".into());
        }
        Ok(LineItem {
            product_id: product_id.to_string(),
            qty,
            unit_price_cents,
        })
    }

    pub fn subtotal(&self) -> u64 {
        self.qty as u64 * self.unit_price_cents
    }
}

#[derive(PartialEq)]
enum OrderStatus {
    Pending,
    Placed,
}

pub struct Order {
    id: String,
    lines: Vec<LineItem>,
    status: OrderStatus,
}

impl Order {
    pub fn create(id: &str) -> Self {
        Order {
            id: id.to_string(),
            lines: Vec::new(),
            status: OrderStatus::Pending,
        }
    }

    /// One method: enforces all invariants atomically or returns Err.
    pub fn place(&mut self, items: Vec<(&str, u32, u64)>) -> Result<(), String> {
        if self.status != OrderStatus::Pending {
            return Err("Order already placed".into());
        }
        if items.is_empty() {
            return Err("Order must have at least one item".into());
        }

        let new_lines: Result<Vec<LineItem>, _> = items
            .into_iter()
            .map(|(id, qty, price)| LineItem::new(id, qty, price))
            .collect();
        let new_lines = new_lines?;

        if new_lines.iter().map(|l| l.subtotal()).sum::<u64>() == 0 {
            return Err("Total must be positive".into());
        }

        self.lines = new_lines;
        self.status = OrderStatus::Placed;
        Ok(())
    }

    pub fn total(&self) -> u64 {
        self.lines.iter().map(|l| l.subtotal()).sum()
    }
}

// Caller: load one aggregate, call one method, persist the result
// order.place(cart_items)?;
// order_repository.save(&order).await?;
// Side effects in other aggregates are triggered via domain events.
```
