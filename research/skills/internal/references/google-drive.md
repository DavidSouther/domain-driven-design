# Google drive

The org document store. First stop for documents, spreadsheets, and presentations that live outside the wiki.

## What it provides

- **Google Drive search**: file hits with id, type, and owner, filterable by file type.
- **Google Drive fetch**: the file content, or extracted text for binary formats, given a file id.

## MCP / connector capabilities

The Anthropic Google Drive connector exposes `search_files` and `read_file_content`. Additional capabilities (`get_file_metadata`, `list_recent_files`, and `download_file_content`) enable richer access when you need it. If this connector is not the one installed, probe the configured Drive MCP for this org.

## Auth

Google OAuth consent. The connector holds the session after consent completes; see [`auth.md`](auth.md). No env var for the OAuth path. If OAuth is not completed, the Drive capabilities are Not-Available.

## Contract mapping

- *Google Drive search* → `search_files` with the query and optional type filter. Returns file hits with id, type, owner.
- *Google Drive fetch* → `read_file_content` by file id (`download_file_content` for raw bytes). Returns file content or extracted text.

## Smoke-test

Search a known doc title, confirm hits carry id/type/owner, then read that file's content by id. A 401 means re-authenticate (an expiry trigger, see [`auth.md`](auth.md)).
