Model a small ordering domain with three things and make their differing natures explicit in the code:

1. a `Batch` that has a stable identity which persists as its state changes over
   time,
2. a `Money` amount-and-currency that has no identity — any two with the same
   amount and currency are interchangeable, and
3. an `allocate` operation that distributes an order line across several `Batch`es
   and belongs to no single batch.

Show all three.
Make clear in the code which has identity, which is a value compared by its fields, and where the cross-batch operation lives.
