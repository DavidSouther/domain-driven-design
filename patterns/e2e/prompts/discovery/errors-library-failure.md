I'm designing the public API of a library function that can fail three different
ways, and the caller needs to react differently to each — retry one, surface
another, give up on the third. I'm deciding between a tagged error the caller can
match on and a single error with a message string. Which `patterns:*` skill applies?
