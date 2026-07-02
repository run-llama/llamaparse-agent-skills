---
name: llamacloud-index
description: Use this skill whenever a question should be answered from documents stored in a LlamaCloud Index v2 knowledge base — retrieving passages, locating indexed files, or searching indexed content through the LlamaParse Platform REST API with curl. Teaches agentic retrieval — navigating an index like a file system instead of one-shot RAG.
compatibility: Needs a `LLAMA_CLOUD_API_KEY` defined within the environment, `curl`, and (recommended) `jq`. EU-region accounts use `api.cloud.eu.llamaindex.ai` instead of `api.cloud.llamaindex.ai`.
license: MIT
metadata:
  author: LlamaIndex
  version: "0.1.0"
---

# LlamaCloud Index v2 — Agentic Retrieval Guide

Answer questions from documents stored in [Index v2](https://developers.llamaindex.ai/llamaparse/cloud-index-v2/getting_started/), the managed knowledge base of the LlamaParse Platform. Every operation is a single authenticated HTTP call, so from a shell the cheapest interface is `curl` + `jq`: you can compose calls, batch independent lookups into one command, and bound exactly how much output enters the conversation.

Index v2 is built for **agentic retrieval**: beyond semantic search, it gives you file-system-like access to the underlying documents (PDFs, Office documents, images, and other unstructured files). This skill is about using that access well — navigating the index the way you would a file system, instead of firing a single one-shot RAG query and hoping the top results contain the answer.

## Setup

```bash
export LLAMA_BASE="https://api.cloud.llamaindex.ai/api/v1"   # EU accounts: https://api.cloud.eu.llamaindex.ai/api/v1
AUTH=(-H "Authorization: Bearer $LLAMA_CLOUD_API_KEY" -H "Content-Type: application/json")
```

If a call returns `401`/`403`, ask the user to check `LLAMA_CLOUD_API_KEY` (and the region) — do not retry in a loop.

## The API

| Operation | Call | Key body fields |
|---|---|---|
| List indexes | `GET /indexes` | — |
| Retrieve passages | `POST /retrieval/retrieve` | `index_id`, `query`, `top_k`, `rerank` (`{enabled, top_n}`, enabled by default), `score_threshold`, `static_filters`, `custom_filters` |
| Find files | `POST /retrieval/files/find` | `index_id`, `file_name_contains` (substring, recommended) or `file_name` (exact) |
| Grep a file | `POST /retrieval/files/grep` | `index_id`, `file_id`, `pattern` (regex), `context_chars` |
| Read a file | `POST /retrieval/files/read` | `index_id`, `file_id`, `offset`, `max_length` (chars; omit for full file) |

`file_id` values come from the find and retrieve responses. Full parameter reference: [retrieval](https://developers.llamaindex.ai/llamaparse/cloud-index-v2/retrieval/) · [file operations](https://developers.llamaindex.ai/llamaparse/cloud-index-v2/file_operations/).

## Step 0 — Pick an Index

Discover once per conversation, not before every query:

```bash
curl -s "${AUTH[@]}" "$LLAMA_BASE/indexes" | jq '.items[] | {id, name, description}'
```

If more than one index plausibly matches the user's question, ask the user which one to use — do not silently query the wrong knowledge base. If the user already gave you an index ID, skip discovery entirely.

## The Agentic Retrieval Loop

Treat the index like a file system you can explore, not a black box you query once:

1. **Discover** — `GET /indexes` to find the right index.
2. **Locate** — `find` to identify the files relevant to the question.
3. **Search** — `grep` for exact patterns within a file.
4. **Retrieve** — `retrieve` for hybrid (sparse + dense) semantic search.
5. **Inspect** — `read` a bounded window of a file when you need surrounding context.

You rarely need all five steps for one question. The skill is choosing the right entry point (below) and iterating: a first retrieval that names a promising document is a reason to grep inside it, not a reason to stop.

## Choosing the Right Call

| Situation | Start with |
|---|---|
| Open or conceptual question ("what does the report say about churn?") | `retrieve` |
| Question spans multiple documents or you don't know the wording used | `retrieve` |
| Looking for an exact term, identifier, figure, or section heading in a known file | `grep` |
| The user names or implies a specific document ("in the Q3 report…") | `find`, then grep/retrieve within it |
| You need continuous context around a passage you already located | `read` with `offset`/`max_length` |

Rules of thumb:

- **`retrieve` matches meaning; `grep` matches patterns.** Use retrieval when you know what you mean but not how the document phrases it. Use grep when you know the literal string (a product name, an account code, "Section 4.2").
- **Verification flows are grep-shaped.** "Does the contract mention X?" is a grep in the located file, not a retrieval.
- **Scope retrieval to one file with a filter** instead of reading it whole: `"static_filters": {"parsed_directory_file_id": {"operator": "eq", "value": "<file-id>"}}` runs semantic search inside just that document.
- **Bound every call.** Set `top_k` for retrieval (and `rerank.top_n` to cap what the reranker returns), `context_chars` for grep, `offset`/`max_length` for reads. Never let an unbounded response into the conversation.

## Working Examples

```bash
# Retrieve passages (bounded, with file and page provenance)
curl -s "${AUTH[@]}" -X POST "$LLAMA_BASE/retrieval/retrieve" -d '{
  "index_id": "<index-id>", "query": "carbon intensity targets", "top_k": 5
}' | jq -r '.results[] | "== file \(.static_fields.parsed_directory_file_id) pp.\(.static_fields.page_range_start)-\(.static_fields.page_range_end) score \(.score)\n\(.content)"'

# Locate a document by name substring
curl -s "${AUTH[@]}" -X POST "$LLAMA_BASE/retrieval/files/find" \
  -d '{"index_id": "<index-id>", "file_name_contains": "quarterly"}' | jq '.items[] | {file_id, file_name}'

# Grep it — context comes back with the match, no follow-up read needed
curl -s "${AUTH[@]}" -X POST "$LLAMA_BASE/retrieval/files/grep" \
  -d '{"index_id": "<index-id>", "file_id": "<file-id>", "pattern": "revenue|profit", "context_chars": 200}' \
  | jq -r '.items[] | "[\(.start_char)-\(.end_char)] \(.content)"'

# Read a window around a grep hit (never the whole file by default)
curl -s "${AUTH[@]}" -X POST "$LLAMA_BASE/retrieval/files/read" \
  -d '{"index_id": "<index-id>", "file_id": "<file-id>", "offset": 12000, "max_length": 4000}' | jq -r '.content'
```

Batch independent lookups into one command instead of one call per turn — several greps or retrievals in a single `for`-loop with labeled output cost one round-trip, not five.

## Grounding Answers

Every claim in your answer must be backed by content you actually retrieved:

- Quote or paraphrase **only** from the returned passages and file contents, and cite the source — retrieval results carry the file ID and page range (`static_fields.page_range_start`/`_end`) for exactly this purpose.
- Do not fill gaps with prior knowledge. If the results only partially answer the question, retrieve again with a refined query or grep the relevant file — don't improvise the rest.
- If the index does not contain the answer, say so explicitly rather than answering from general knowledge. Offer to answer without the index if that is still useful.
- When passages conflict, surface the conflict and the source files instead of picking one silently.

## Common Pitfalls

- **Don't paste whole files into context.** An unbounded `read` on a large document floods the conversation with content you'll pay for on every subsequent turn. If you need one fact, grep; if you need the relevant passages, retrieve (optionally filtered to the file); if you need a region, read a window. Read a file in full only when nothing narrower can answer the question.
- **Don't one-shot RAG.** A single retrieve call is the floor, not the ceiling. If the top passages don't answer the question, refine the query, or pivot: use the file IDs surfaced by retrieval to grep or inspect the most promising document.
- **Don't grep for paraphrases.** Grep matches patterns, not meaning. If your grep for the user's phrasing comes back empty, that does not mean the answer is absent — switch to `retrieve`.
- **Don't dump raw JSON.** Always pipe through `jq` to project just the fields you need; a raw retrieval response is mostly metadata you don't want in context.
- **Don't repeat identical calls.** Re-running the same retrieval or grep returns the same results. Change the query, the pattern, or the call.
- **Don't guess the index.** Querying the wrong knowledge base produces confidently wrong, well-cited answers. When multiple indexes could match, ask.
- **Don't answer around missing content.** Absence of results is information: report what you searched and what wasn't there.

## No Shell Access?

If you are running in an environment without a shell, the same operations are exposed as tools by the [LlamaParse MCP server](https://developers.llamaindex.ai/llamaparse/integrations/mcp/) (`https://mcp.llamaindex.ai/mcp`, or scoped to one index at `/index/{indexId}/mcp`) — the workflow and discipline above apply unchanged.
