# Bootstrap and service: TypeScript reference

The four layers and their mandates:

| Layer | Mandate |
|---|---|
| **Domain** | Pure business rules, aggregates, value objects, domain services, errors as values; no I/O |
| **Application Service** | Orchestrates one use scenario: parses input, calls domain + repository ports, returns typed results; no HTTP or DB knowledge |
| **Adapter** | Implements a port interface defined by the service layer; translates protocol details (HTTP status codes, command-line tool flags) to/from service calls; no business logic |
| **Composition Root** | The only place that imports concrete classes; constructs and injects all dependencies; runs once at startup |

```typescript
// domain.ts — pure logic, no I/O
export type Order = { id: string; total: number };
export type InsufficientFunds = { kind: "InsufficientFunds"; balance: number };

export function placeOrder(order: Order, balance: number): Order | InsufficientFunds {
  if (balance < order.total) return { kind: "InsufficientFunds", balance };
  return order;
}

// ports.ts — interfaces owned by the service layer (not the adapter)
export interface OrderRepository {
  getBalance(customerId: string): Promise<number>;
}

// service.ts — application service: orchestrates, does not own rules
export class OrderService {
  constructor(private readonly repo: OrderRepository) {}

  async place(raw: unknown): Promise<Order | InsufficientFunds | ParseError> {
    const parsed = parseOrder(raw); // parse-don't-validate
    if (parsed.kind === "ParseError") return parsed;
    const balance = await this.repo.getBalance(parsed.customerId);
    return placeOrder(parsed, balance); // domain function owns the rule
  }
}

// adapter.ts — thin HTTP adapter; maps protocol, calls service
async function handlePlaceOrder(req: Request, res: Response) {
  const result = await orderService.place(req.body);
  if (result.kind === "InsufficientFunds") return res.status(422).json(result);
  if (result.kind === "ParseError") return res.status(400).json(result);
  res.status(201).json(result);
}

// bootstrap.ts — Composition Root; the only file that knows about Postgres
const repo = new PostgresOrderRepository(process.env.DATABASE_URL);
const orderService = new OrderService(repo);
app.post("/orders", handlePlaceOrder);
```
