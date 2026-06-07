# Citations Reference

Every factual claim carries its source. How you attach it depends on where the answer lands. In a chat, especially on a phone, the source is a tappable link in the prose. In a saved report, it can be a fuller list. Default to the chat form.

## In Chat: Inline Links (default)

Name the source in the link text and place it right after the claim it supports. The reader taps a word, not a footnote number, and never scrolls to a bibliography.

```text
The default timeout is 30 seconds ([reqwest docs](https://docs.rs/reqwest)).
```

Rules:

- **Link text names the source**, not "here" or "this": `[reqwest docs]`, `[the Node release schedule]`, `[Stripe's pricing page]`.
- **One link per claim**, placed at the claim. If two sources back one claim, link both: "*...is the default ([A](url), [B](url))*".
- **No numbered footnotes, no trailing "Sources" section** in a chat message. Those belong to the saved-report form.
- **Quote sparingly and exactly.** Three exact words beat a reworded paragraph. Put the quote in the link or right beside it.

## Citing a Connector

When a claim comes from the user's own authorized account, cite it by name and by a stable handle so the user knows the exact item. There is no public URL, so the handle does the work.

```text
The kickoff is Thursday 10am (calendar invite "Q3 Kickoff").
You already replied yes (Gmail thread with Dana, May 3).
```

Use the item's real identifier where one exists: a Linear ticket key (NOM-412), a Slack channel and date, an email subject and sender, a Drive file name. If the connector exposes a deep link, make the handle a real markdown link; otherwise the named handle stands alone in parentheses, with no empty `[ ]` brackets (those render as a broken link).

## In a Saved Report: Numbered List (enhancement)

Only when writing to a file. Follow a loose IEEE style: a number in square brackets after the statement, assigned sequentially at first use, reused for repeat references. Mark public web sources `[Online]` and connector sources `[Connector]`.

```text
The default timeout is 30 seconds [1].

## Sources
[1] reqwest. "Client docs." 2026-01. [Online]. Available: https://docs.rs/reqwest
[2] Linear. "NOM-412." [Connector].
```

This format is heavy for a phone screen. Use it only in a document the user will keep, never in a chat reply.
