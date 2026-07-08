# Errors: typed vs untyped, python reference

Each language has its own grammar for failure.
The pattern is constant: typed at library boundaries, stringly at app boundaries, with a translation step between.
The idioms differ.
Use the variant native to your language; do not transliterate one into another.

A shared scenario runs through every example: a `users` library that fetches a user by id, and an app that exposes that library through an HTTP handler.

### Library, typed error hierarchy

Python's typed errors are exception subclasses.
Each subclass is a distinct variant; instance attributes carry the variant data.
A single base class for the library lets callers `except UsersError` for a coarse handler, while specific subclasses serve precise dispatch.

```python
# users/errors.py
class UsersError(Exception):
    """Base class for users library errors."""


class NetworkError(UsersError):
    """Underlying transport failed."""


class NotFoundError(UsersError):
    def __init__(self, user_id: str) -> None:
        super().__init__(f"user {user_id} not found")
        self.user_id = user_id


class ParseError(UsersError):
    def __init__(self, field: str, raw: str) -> None:
        super().__init__(f"malformed payload: field {field!r} had value {raw!r}")
        self.field = field
        self.raw = raw


# users/fetch.py
import httpx
from . import errors

def fetch_user(client: httpx.Client, user_id: str) -> User:
    try:
        res = client.get(f"/users/{user_id}")
    except httpx.HTTPError as cause:
        raise errors.NetworkError("transport failed") from cause

    if res.status_code == 404:
        raise errors.NotFoundError(user_id)

    raw = res.json()
    email = raw.get("email")
    if not isinstance(email, str):
        raise errors.ParseError(field="email", raw=repr(email))

    return User(**raw)
```

Each `raise ... from cause` preserves the underlying exception in `__cause__`.
Callers may dispatch on the subclass; logging captures the full chain via `logging.exception` or `traceback.format_exception`.

### App, stringly error

The HTTP handler catches the typed exceptions at the boundary and translates them into a user-facing string.
The app does not propagate `UsersError`; it formats and either returns or logs.

```python
# app/http/users.py
import logging
from users import errors, fetch_user

log = logging.getLogger(__name__)

@app.get("/users/{user_id}")
def get_user(user_id: str):
    try:
        return fetch_user(client, user_id)
    except errors.NotFoundError:
        return Response(status=404, body=f"User {user_id} does not exist.")
    except errors.NetworkError:
        log.exception("loading user %s: upstream network failure", user_id)
        return Response(status=502, body="Upstream user service is unreachable.")
    except errors.ParseError:
        log.exception("loading user %s: malformed payload", user_id)
        return Response(status=502, body="Upstream returned an unexpected response.")
```

The handler is stringly: it produces a human message, no programmatic dispatch beyond the `except` clauses themselves.

### Translation rules

- Always `raise FromTyped(...) from original_exception`.
  The `from` clause sets `__cause__` and keeps the chain intact for `logging.exception` and tracebacks.
- Do not parse error messages with `str(e)` or substring matches.
  The message is for humans.
  Match on the class.
- Resist the temptation to define exceptions inline in the function that raises them.
  Place them in a dedicated module so callers can `from users.errors import NotFoundError`.
