The auth-handler change below is finished: static checks pass, the unit tests are green, and the working directory is clean (everything is committed).
Before I open the PR I want to clean up the code.
Nothing about its behaviour should change.

`auth/handler.py`:

```python
def handle_login(request):
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return error(401)
    token = header[len("Bearer "):]
    user = lookup(token)
    if user is None:
        return error(401)
    if not user.active:
        return error(403)
    if user.role not in ("admin", "member", "viewer"):
        return error(403)
    log_event("login", user.id)
    session = make_session(user)
    return ok(session)

def handle_refresh(request):
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return error(401)
    token = header[len("Bearer "):]
    user = lookup(token)
    return ok(make_session(user)) if user else error(401)

def handle_logout(request):
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return error(401)
    token = header[len("Bearer "):]
    drop_session(token)
    return ok(None)
```

Clean this up before I finalize the task.
