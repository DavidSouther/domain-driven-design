# TypeScript project reference

Toolchain: vite/vitest + biome + strict TypeScript

## Target distinction

Choose the appropriate target before scaffolding:

| Target | Use when | Framework |
|---|---|---|
| **Browser** | UI, React/Vue/Svelte apps | vite + vitest (jsdom) |
| **Server** | Node.js API, command-line tools | vitest (node) |
| **Edge** | Cloudflare Workers, Vercel Edge | vitest (edge-runtime) |

## Required layout

```
<project>/
  package.json
  tsconfig.json
  biome.json
  vite.config.ts        # or vitest.config.ts for server-only
  src/
    index.ts            # main entry point
  tests/
    features/
      <feature>.test.ts # integration/feature tests
    unit/
      <module>.test.ts  # unit tests
```

## Required config files

### `package.json` (minimum)

```json
{
  "name": "my-project",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "test": "vitest run",
    "check": "tsc --noEmit && biome check src tests",
    "format": "biome format --write",
    "lint": "biome lint --write"
  },
  "devDependencies": {
    "@biomejs/biome": "^1.9.0",
    "typescript": "^5.7.0",
    "vite": "^6.0.0",
    "vitest": "^3.0.0"
  }
}
```

### `tsconfig.json` (strict mode required)

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true,
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src", "tests"]
}
```

### `biome.json`

```json
{
  "$schema": "https://biomejs.dev/schemas/1.9.0/schema.json",
  "organizeImports": { "enabled": true },
  "linter": {
    "enabled": true,
    "rules": { "recommended": true }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "lineWidth": 100
  }
}
```

### `vite.config.ts`

```typescript
import { defineConfig } from "vite";

export default defineConfig({
  test: {
    environment: "jsdom",    // change to "node" for server, "edge-runtime" for edge
    include: ["tests/**/*.test.ts"],
  },
});
```

## Validation checklist

- [ ] You have `node` v20+ installed (verify with `node --version`)
- [ ] You have `npm` or `pnpm` installed
- [ ] `package.json` exists with required scripts
- [ ] `tsconfig.json` has `"strict": true`
- [ ] `biome.json` exists
- [ ] `src/` directory exists
- [ ] `tests/features/` directory exists
- [ ] `npm install` exits 0
- [ ] `npm run check` exits 0 (no type errors, no lint errors)
- [ ] `npm test` exits 0

## Scaffolding (if validation fails)

```bash
# New project
npm create vite@latest <name> -- --template vanilla-ts
cd <name>
npm install
npm install --save-dev @biomejs/biome vitest jsdom
mkdir -p tests/features tests/unit

# Verify
npm run check
npm test
```

## Development hooks

| Hook | Command |
|---|---|
| Format | `npx biome format --write <edited-file>` |
| Check | `npm run check` (tsc + biome check) |
| Test | `npm test` |
| Lint | `npx biome lint --write src tests` |

## Feature tests

Feature tests live in `tests/features/`.
For server targets, test HTTP handlers directly.
For browser targets, use a test renderer or a minimal DOM fixture.

```typescript
// tests/features/user-login.test.ts
import { describe, expect, it } from "vitest";
import { createApp } from "../../src/app.js";

describe("user login", () => {
  it("logs in and redirects to dashboard", async () => {
    const app = createApp({ db: testDb() });
    await app.createUser({ email: "a@example.com", password: "secret" });

    const res = await app.request("/login", {
      method: "POST",
      body: new URLSearchParams({ email: "a@example.com", password: "secret" }),
    });

    expect(res.status).toBe(302);
    expect(res.headers.get("location")).toBe("/dashboard");
  });
});
```

## Verification command

```bash
npm run check && npm test
```

Expected: zero TypeScript errors, zero biome errors, all tests pass.
