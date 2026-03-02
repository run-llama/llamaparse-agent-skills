---
name: llamaparse
description: Use this skill when the user asks to parse the content of an unstructured file (PDF, PPTX, DOCX...)
compatibility: Needs a `LLAMA_CLOUD_API_KEY` defined within the environment and the `llama-cloud>=1.0` python library installed.
license: MIT
metadata:
  author: LlamaIndex
  version: "0.1.0"
---

# LlamaParse Skill

Parse unstructured documents (such as PDF, DOCX, PPTX, XLSX) with LlamaParse and extract their contents (text, markdown, images...).

## Initial Setup

When this skill is invoked, respond with:

```
I'm ready to use LlamaParse to parse files. Before we begin, please confirm that:

- `LLAMA_CLOUD_API_KEY` is set as environment variable within the current environment
- `llama-cloud>=1.0` is installed and available within the current python environment

If both of them are set, please provide:

1. One or more files to be parsed
2. Specific parsing options, such as tier, API version, custom prompt, processing options...
3. Any requests you might have regarding the parsed content of the file.

I will produce a python script to run the parsing job and, once you approved its execution, I will report the results back to you based on your request.
```

Then wait for the user's input.

---

## Step 0 — Install `llama-cloud` (optional)

If the user does not have the `llama-cloud` package installed, add it to the current environment by running:

```bash
uv pip install 'llama-cloud>=1.0.0'
```

## Step 1 — Produce a Python Script

Once the user confirms the environment variables are set and provides the necessary details for the parsing job, produce a **python script**.

As a source of truth for the python script, you can:

- Refer to the [example.py](scripts/example.py) script, which covers most of the necessary configurations for LlamaParse
- Refer to the complete LlamaParse Documentation, fetching the `https://developers.llamaindex.ai/python/cloud/llamaparse/api-v2-guide/` page.

### Scripting Best Practices

Follow these guidelines when generating scripts:

#### 1. Always Use the Async Client

Use `AsyncLlamaCloud` (not the sync client) for all parsing operations. Wrap the entry point with `asyncio.run()`.

```python
from llama_cloud import AsyncLlamaCloud
client = AsyncLlamaCloud(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))
```

#### 2. Two-Step Upload → Parse Pattern

Always upload first to get a file ID, then parse using the file ID. Never pass raw file bytes directly to `parse()`.

```python
# Step 1: Upload
file_obj = await client.files.create(file=file_path, purpose="parse")
file_id = file_obj.id

# Step 2: Parse using the file ID
result = await client.parsing.parse(file_id=file_id, ...)
```

If the user already has a file ID (e.g. from a prior upload), skip the upload step and use it directly.

#### 3. Choose the Right Tier

| Tier | When to Use |
|------|-------------|
| `fast` | Speed is the priority; simple documents |
| `cost_effective` | Budget-conscious; straightforward text extraction |
| `agentic` | Complex layouts, tables, mixed content (default recommendation) |
| `agentic_plus` | Advanced analysis, highest accuracy |

Default to `agentic` unless the user specifies otherwise or the document is simple.

#### 4. Always Include the `expand` Parameter

The `expand` parameter controls what content is returned. Omitting it returns minimal data. Always specify exactly what you need:

| Value | Returns |
|-------|---------|
| `text` | Plain text via `result.text_full` |
| `markdown` | Markdown via `result.markdown_full` |
| `items` | Page-level JSON via `result.items.pages` |
| `text_content_metadata` | Per-page text metadata |
| `markdown_content_metadata` | Per-page markdown metadata |
| `items_content_metadata` | Per-page items metadata |
| `images_content_metadata` | Image list with presigned URLs |
| `output_pdf_content_metadata` | Output PDF metadata |
| `xlsx_content_metadata` | Excel-specific metadata |

Only request metadata `*_content_metadata` variants when you need presigned URLs or per-page detail — they increase payload size.

#### 5. Handle None Results Defensively

`result.text_full`, `result.markdown_full`, and `result.items` may be `None` on failure. Always guard against this:

```python
text = result.text_full or ""
markdown = result.markdown_full or ""
```

#### 6. Use Structured Options for Advanced Configuration

Group options using the correct nested keys:

```python
result = await client.parsing.parse(
    tier="agentic",
    version="latest",
    file_id=file_id,
    expand=["markdown"],
    input_options={
        "presentation": {"skip_embedded_data": False},
    },
    output_options={
        "images_to_save": ["screenshot"],
        "markdown": {
            "tables": {"output_tables_as_markdown": True},
            "annotate_links": True,
        },
    },
    processing_options={
        "specialized_chart_parsing": "agentic",
        "ocr_parameters": {"languages": ["en"]},
    },
    agentic_options={
        "custom_prompt": "Extract and summarize the key findings.",
    },
)
```

Use `agentic_options.custom_prompt` whenever the user wants to guide extraction (translation, summarization, structured extraction, etc.).

#### 7. Downloading Images Requires `httpx` and Auth

When `images_content_metadata` is in `expand`, download images via presigned URLs with Bearer auth:

```python
async with httpx.AsyncClient(
    headers={"Authorization": f"Bearer {os.getenv('LLAMA_CLOUD_API_KEY')}"}
) as http:
    response = await http.get(image.presigned_url)
    response.raise_for_status()
    with open(image.filename, "wb") as f:
        f.write(response.content)
```

Add `httpx>=0.28` to the script dependencies when images are requested.

#### 8. Use the `uv` Script Header for Portability

Every generated script should include the inline `uv` script metadata header:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#    "llama-cloud>=1.0.0",
#    "httpx>=0.28",   # only if downloading images
# ]
# ///
```

---

## Step 2 — Execute the Python Script

Once the python script has been produced, you should:

1. Present the script to the user and ask for permissions to run it (depending on the current permissions settings)
2. Once you obtained permission to run, execute the script
3. Explore the results based on the user's requests

> In order to run python scripts, it is highly recommended to use `uv`.
