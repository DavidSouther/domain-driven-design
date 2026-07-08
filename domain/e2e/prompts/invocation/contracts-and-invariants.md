Below is the current state of `docs/ddd/contexts/order-management.md`:

```markdown
# Order Management

**Classification:** Core
**Responsibilities:** Accepting customer orders, validating line items, persisting them for fulfilment.
**Consumes:** Customer profile data from the Customer context.
**Produces:** `OrderPlaced` events consumed by the Fulfilment context.
```

A new operation needs a contract: `place_order(customer_id, line_items)`.
It must reject orders with zero line items, reject orders where any line item has zero or negative quantity, and emit `OrderPlaced` on success.

Append the contract block for this operation the way the contracts-and-invariants ability prescribes.
Produce the full file content as it should look after the append, with the existing content preserved.
