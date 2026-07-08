# Errors: typed vs untyped, rust reference

Each language has its own grammar for failure.
The pattern is constant: typed at library boundaries, stringly at app boundaries, with a translation step between.
The idioms differ.
Use the variant native to your language; do not transliterate one into another.

A shared scenario runs through every example: a `users` library that fetches a user by id, and an app that exposes that library through an HTTP handler.

### Library, typed error with `thiserror`

In Rust the convention is hard.
Library crates derive their error type with [`thiserror`](https://docs.rs/thiserror); app crates use [`anyhow`](https://docs.rs/anyhow).
The same crate authors maintain both, and the division is intentional.

```rust
// users/src/error.rs
use thiserror::Error;

#[derive(Debug, Error)]
pub enum FetchError {
    #[error("network failure")]
    Network(#[from] reqwest::Error),

    #[error("user {0} not found")]
    NotFound(String),

    #[error("malformed payload: field `{field}` had value `{raw}`")]
    Parse { field: String, raw: String },
}

// users/src/fetch.rs
pub async fn fetch_user(client: &Client, id: &str) -> Result<User, FetchError> {
    let res = client.get(format!("/users/{id}")).send().await?;
    if res.status() == StatusCode::NOT_FOUND {
        return Err(FetchError::NotFound(id.to_owned()));
    }
    let raw: RawUser = res.json().await?;
    raw.try_into().map_err(|(field, raw)| FetchError::Parse { field, raw })
}
```

`#[from]` lets `?` lift `reqwest::Error` into `FetchError::Network` automatically.
Each variant is exhaustive, pattern-matchable, and carries its own data.

### Application, stringly error with `anyhow`

In a binary crate, `anyhow::Error` collapses every error type into one.
The handler does not match on variants; it adds context with `.context()` and lets the framework render the chain.

```rust
// app/src/http/users.rs
use anyhow::Context;

async fn get_user(Path(id): Path<String>, State(client): State<Client>) -> impl IntoResponse {
    match users::fetch_user(&client, &id).await {
        Ok(user) => Json(user).into_response(),
        Err(users::FetchError::NotFound(_)) => (
            StatusCode::NOT_FOUND,
            format!("User {id} does not exist."),
        ).into_response(),
        Err(e) => {
            let report: anyhow::Error = anyhow::Error::new(e)
                .context(format!("loading user {id}"));
            tracing::error!("{report:#}");
            (StatusCode::BAD_GATEWAY, "Upstream user service unavailable.").into_response()
        }
    }
}
```

The code explicitly matches the `NotFound` variant because the response code differs.
Every other variant collapses into `502`, with the structured cause logged via `anyhow`'s chain formatting (`{:#}`).

### Translation rules

- A library crate that depends on `anyhow` is a smell.
  The dependency means the crate is throwing away type information its callers must recover.
- Never `Err(anyhow!("not found"))` from a library.
  Define the variant.
- Use `?` aggressively in app code; use `.context("operation X")` to thread human-readable breadcrumbs through the cause chain.
