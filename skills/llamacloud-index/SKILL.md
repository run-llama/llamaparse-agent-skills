---
name: llamacloud-index
description: Use this skill whenever a question should be answered from documents stored in a LlamaCloud Index v2 knowledge base — retrieving passages, locating indexed files, or searching indexed content through the LlamaParse MCP Index v2 tools (retrieveFromIndex, findFilesInIndex, grepFileFromIndex...). Teaches agentic retrieval — navigating an index like a file system instead of one-shot RAG.
compatibility: Needs authenticated access to the LlamaParse MCP server — `https://mcp.llamaindex.ai/mcp` (unified) or `https://mcp.llamaindex.ai/index/{indexId}/mcp` (scoped to a single index). Authentication is OAuth-based; no API key required.
license: MIT
metadata:
  author: LlamaIndex
  version: "0.1.0"
---

# LlamaCloud Index v2 — Agentic Retrieval Guide

Answer questions from documents stored in [Index v2](https://developers.llamaindex.ai/llamaparse/cloud-index-v2/getting_started/), the managed knowledge base of the LlamaParse Platform, using the Index v2 tools exposed by the [LlamaParse MCP server](https://developers.llamaindex.ai/llamaparse/integrations/mcp/).

Index v2 is built for **agentic retrieval**: beyond semantic search, it gives you file-system-like access to the underlying documents (PDFs, Office documents, images, and other unstructured files). This skill is about using that access well — navigating the index the way you would a file system, instead of firing a single one-shot RAG query and hoping the top results contain the answer.

## Authentication

All tools require a valid session. The MCP server uses OAuth — no API key is needed, and authentication happens in the MCP client on first use. If a tool call returns an authentication error, ask the user to re-authenticate before retrying. Do not retry automatically without prompting the user.

## The Tools

| Tool | What it does | Key inputs |
|---|---|---|
| `getUserProjects` | Lists the project IDs associated with your account | — |
| `listIndexes` | Lists the indexes you can query — vector-indexed directories whose files you can find, read, and grep, and over which you can perform retrieval | `projectId` (optional) |
| `findFilesInIndex` | Locates files within an index by exact name or name substring | `fileNameContains` (substring match, recommended) or `fileName` (exact match) |
| `readFileFromIndex` | Reads the content of a file in an index — the whole file, or a window of it | `fileId`, `offset` (chars), `maxLength` (chars) |
| `grepFileFromIndex` | Greps a file's content for a pattern | `fileId`, `pattern`, `contextChars` (context around each match), `limit` (max matches) |
| `retrieveFromIndex` | Performs hybrid (sparse + dense) retrieval over an index | `query`, `topK` (default 10), `rerankTopN` (enables reranking; off if omitted) |

Every tool accepts an optional `projectId` and falls back to your default project when it is omitted. The file/retrieval tools take an `indexId` (as returned by `listIndexes`) — except on the scoped `/index/{indexId}/mcp` endpoint, where the index is inherited from the route. `fileId` values come from `findFilesInIndex`.

## Step 0 — Pick an Index

How you pick the index depends on which endpoint the client is connected to:

- **Scoped endpoint (`https://mcp.llamaindex.ai/index/{indexId}/mcp`)** — the index ID is inherited from the route and is already in context. Skip discovery entirely and go straight to searching. This is the recommended setup when a workflow always targets one knowledge base.
- **Unified endpoint (`https://mcp.llamaindex.ai/mcp`)** — call `listIndexes` to discover the indexes you can query. It searches your default project unless you pass a `projectId`; if the work spans projects, call `getUserProjects` to get the project IDs you can pass. If more than one index plausibly matches the user's question, ask the user which one to use — do not silently query the wrong knowledge base.

Discover once per conversation. Do not re-run `listIndexes` before every query; reuse the index you already identified unless the user changes topic to a different corpus.

## The Agentic Retrieval Loop

Treat the index like a file system you can explore, not a black box you query once:

1. **Discover** — `listIndexes` to find the right index (skip on a scoped endpoint).
2. **Locate** — `findFilesInIndex` to find the files relevant to the question.
3. **Inspect** — `readFileFromIndex` to look at a specific file's contents when you need it.
4. **Search** — `grepFileFromIndex` to find exact patterns within indexed files.
5. **Retrieve** — `retrieveFromIndex` for hybrid semantic search over the index.

You rarely need all five steps for one question. The skill is choosing the right entry point (below) and iterating: a first retrieval that names a promising document is a reason to `grepFileFromIndex` inside it, not a reason to stop.

## Choosing the Right Tool

| Situation | Start with |
|---|---|
| Open or conceptual question ("what does the report say about churn?") | `retrieveFromIndex` |
| Question spans multiple documents or you don't know the wording used | `retrieveFromIndex` |
| Looking for an exact term, identifier, figure, or section heading in a known file | `grepFileFromIndex` |
| The user names or implies a specific document ("in the Q3 report…") | `findFilesInIndex`, then grep/read within it |
| You need continuous context around a passage you already located | `readFileFromIndex` |

Rules of thumb:

- **`retrieveFromIndex` matches meaning; `grepFileFromIndex` matches patterns.** Use retrieval when you know what you mean but not how the document phrases it. Use grep when you know the literal string (a product name, an account code, "Section 4.2") — a semantic query for an exact identifier wastes a retrieval on something grep answers precisely.
- **Verification flows are grep-shaped.** "Does the contract mention X?" is a grep in the located file, not a retrieval.
- **Find files by substring.** Prefer `fileNameContains` over exact `fileName` in `findFilesInIndex` unless you know the exact file name — user-supplied names rarely match verbatim.
- **Bound every call.** For grep, set `contextChars` so the surrounding text comes back with each match (no follow-up read needed) and `limit` to cap the number of matches. For retrieval, `topK` defaults to 10 — raise it only when recall genuinely matters, and set `rerankTopN` when precision matters (reranking is disabled unless you ask for it).
- **Read in windows, not in full.** `readFileFromIndex` takes `offset` and `maxLength` in characters: when a grep match or retrieved passage points at a region, read that window instead of the whole file. Full reads are the last resort — e.g. the answer depends on document-wide structure or the file is short.

## Grounding Answers

Every claim in your answer must be backed by content you actually retrieved:

- Quote or paraphrase **only** from the passages and file contents returned by the tools, and say which file (and where in it, when known) each claim comes from.
- Do not fill gaps with prior knowledge. If the retrieved passages only partially answer the question, retrieve again with a refined query or grep the relevant file — don't improvise the rest.
- If the index does not contain the answer, say so explicitly rather than answering from general knowledge. Offer to answer without the index if that is still useful.
- When passages conflict, surface the conflict and the source files instead of picking one silently.

## Common Pitfalls

- **Don't paste whole files into context.** `readFileFromIndex` without `offset`/`maxLength` on a large document floods the conversation with content you'll pay for on every subsequent turn. If you need one fact from a file, `grepFileFromIndex` it; if you need the relevant passages, `retrieveFromIndex`; if you need a region, read a bounded window. Read a file in full only when nothing narrower can answer the question.
- **Don't one-shot RAG.** A single `retrieveFromIndex` call is the floor, not the ceiling. If the top passages don't answer the question, refine the query, or pivot: use the file names surfaced by retrieval to grep or inspect the most promising document.
- **Don't grep for paraphrases.** `grepFileFromIndex` matches patterns, not meaning. If your grep for the user's phrasing comes back empty, that does not mean the answer is absent — switch to `retrieveFromIndex`.
- **Don't repeat identical calls.** Re-running the same retrieval or grep returns the same results. Change the query, the pattern, or the tool.
- **Don't guess the index.** Querying the wrong knowledge base produces confidently wrong, well-cited answers. When multiple indexes could match, ask.
- **Don't answer around missing content.** Absence of results is information: report what you searched and what wasn't there.
