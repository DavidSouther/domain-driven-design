I keep null-checking `customer.shippingAddress` everywhere it gets used. It
is only ever set after the customer confirms their cart, but the type does not
say so. Which `patterns:*` skill applies?
