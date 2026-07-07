# Hardcover

Reviews and reading-community signal. Replaces the retired Goodreads API. Use for "what do other readers say about this book?", rating snippets, comparable-titles queries.

## What it provides

- **Reader reviews** for cataloged books.
- **Ratings and ranked-list data**: what users have shelved, rated, or compared.
- **Comparable-titles** queries.

## Mcp option

None first-party. Use HTTP.

## Http fallback

- Base URL: `https://api.hardcover.app/v1/graphql`
- Auth: API key, sent as `Authorization: Bearer <HARDCOVER_API_KEY>`. Obtain at the Hardcover account settings page.
- GraphQL endpoint; queries select fields explicitly. See the Hardcover schema reference for the full type surface.

Example query:

```graphql
query { books(where: { isbn_13: "9780321125217" }) {
  id title users_reviews { rating review_text } } }
```

## Query shapes

- *"Reader reviews of the Stripe Press edition of The Soul of a New Machine"*: GraphQL query selecting `users_reviews` filtered by ISBN.
- *"What are people comparing this book to"*: `comparable_titles` field.
- *"Average rating for this book"*: aggregated rating field.

## Licensing

Hardcover reviews are user-generated; the platform terms govern redistribution. **Cite-and-link** rather than transcribe reviews verbatim. Aggregated rating data is generally safe to summarize.

## Failure modes

- **API key missing**: 401. Set `HARDCOVER_API_KEY`.
- **Schema drift**: GraphQL schema evolves; refresh the schema reference when fields stop resolving.
- **Empty review set**: newer or obscure titles may have no reviews yet. The practice skill returns the empty result rather than failing.
