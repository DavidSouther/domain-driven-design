`HttpRequest` has a five-argument constructor — method, url, headers, body, timeout —
and callers keep swapping arguments and forgetting which are required, sometimes
producing a half-initialized request. I want required-vs-optional made explicit at
construction and validation to run before the object exists. Which `patterns:*`
skill applies?
