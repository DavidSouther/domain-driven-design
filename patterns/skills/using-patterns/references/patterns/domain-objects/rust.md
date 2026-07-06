# Entities, value objects, and domain service functions, Rust reference

```rust
use std::cmp::Ordering;

// VALUE OBJECT — no identity, equality by value, all fields public and cloneable
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OrderLine {
    pub order_id: String,
    pub sku: String,
    pub qty: u32,
}

impl OrderLine {
    /// "Mutation" produces a new instance; the original is unchanged.
    pub fn with_qty(&self, qty: u32) -> Self {
        OrderLine { qty, ..self.clone() }
    }
}

// ENTITY — identity via id, mutable state, equality by id
pub struct Batch {
    id: String,
    sku: String,
    pub eta: chrono::NaiveDate,
    available: u32,
}

impl Batch {
    pub fn new(id: &str, sku: &str, eta: chrono::NaiveDate, available: u32) -> Self {
        Batch {
            id: id.to_string(),
            sku: sku.to_string(),
            eta,
            available,
        }
    }

    pub fn id(&self) -> &str {
        &self.id
    }

    pub fn can_allocate(&self, line: &OrderLine) -> bool {
        self.sku == line.sku && self.available >= line.qty
    }

    pub fn allocate(&mut self, line: &OrderLine) -> Result<(), String> {
        if !self.can_allocate(line) {
            return Err("Cannot allocate".into());
        }
        self.available -= line.qty; // state changes; identity stays the same
        Ok(())
    }
}

// Entities compare by identity, not by field values
impl PartialEq for Batch {
    fn eq(&self, other: &Self) -> bool {
        self.id == other.id
    }
}

// DOMAIN SERVICE FUNCTION — stateless; coordinates logic spanning multiple entities
pub fn allocate(line: &OrderLine, batches: &mut [Batch]) -> Result<String, String> {
    // Sort eligible batches by earliest ETA
    let mut eligible: Vec<&mut Batch> = batches
        .iter_mut()
        .filter(|b| b.can_allocate(line))
        .collect();

    eligible.sort_by_key(|b| b.eta);

    let chosen = eligible
        .into_iter()
        .next()
        .ok_or_else(|| format!("Out of stock: {}", line.sku))?;

    chosen.allocate(line)?;
    Ok(chosen.id().to_string())
}
```
