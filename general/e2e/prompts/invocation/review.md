You are about to claim the following change complete. Run a review pass
first, and produce the review output directly in your reply. This environment
has no file system and no tools — do not call tools; write your review inline.

The change carries concerns in more than one domain: code correctness and the
longevity of its comments. Review it accordingly.

Task: "Add an `is_admin: bool` field to the `User` struct and surface it on
the `/users/:id` JSON response."

Diff:

```diff
--- a/app/models.py
+++ b/app/models.py
@@ -8,12 +8,16 @@ from datetime import datetime

 @dataclass
 class User:
+    """A user record.
+
+    Constructed by routes.get_user and by tests.test_models. Update both
+    call sites when adding a field.
+    """
     id: int
     name: str
     email: str
+    is_admin: bool

-def format_timestamp(ts: int) -> str:
-    return datetime.utcfromtimestamp(ts).isoformat()
+def fmt_ts(ts: int) -> str:
+    # fast path: assume ts is always UTC seconds
+    return datetime.utcfromtimestamp(ts).isoformat()

--- a/app/routes.py
+++ b/app/routes.py
@@ -22,6 +22,7 @@ def get_user(user_id: int):
     user = repo.find(user_id)
     return jsonify({
         "id": user.id,
         "name": user.name,
         "email": user.email,
+        "is_admin": user.is_admin,
     })

--- a/tests/test_models.py
+++ b/tests/test_models.py
@@ -3,8 +3,3 @@ from app.models import User

 def test_user_has_email():
     u = User(1, "a", "a@example.com")
     assert u.email == "a@example.com"
-
-def test_format_timestamp():
-    assert format_timestamp(0) == "1970-01-01T00:00:00"
```
