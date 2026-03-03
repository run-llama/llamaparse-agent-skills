---
name: llamaparse
description: Use this skill when the user asks to parse the content of an unstructured file (PDF, PPTX, DOCX...)
compatibility: Needs a `LLAMA_CLOUD_API_KEY` defined within the environment and the `@llamaindex/llama-cloud@latest` typescript library installed.
license: MIT
metadata:
  author: LlamaIndex
  version: "1.0.0"
---

# LlamaParse Skill

Parse unstructured documents (such as PDF, DOCX, PPTX, XLSX) with LlamaParse and extract their contents (text, markdown, images...).

## Initial Setup

When this skill is invoked, respond with:

```
I'm ready to use LlamaParse to parse files. Before we begin, please confirm that:

- `LLAMA_CLOUD_API_KEY` is set as environment variable within the current environment
- `@llamaindex/llama-cloud@latest` is installed and available within the current Node environment

If both of them are set, please provide:

1. One or more files to be parsed
2. Specific parsing options, such as tier, API version, custom prompt, processing options...
3. Any requests you might have regarding the parsed content of the file.

I will produce a Typescript script to run the parsing job and, once you approved its execution, I will report the results back to you based on your request.
```

Then wait for the user's input.

---

## Step 0 — Install `llama-cloud` (optional)

If the user does not have the `@llamaindex/llama-cloud` package installed, add it to the current environment by running:

```bash
npm install @llamaindex/llama-cloud@latest
```

## Step 1 — Produce a Typescript Script

Once the user confirms the environment variables are set and provides the necessary details for the parsing job, produce a **typescript script**.

As a source of truth for the TS script, you can:

- Refer to the [example.ts](scripts/example.ts) script, which covers most of the necessary configurations for LlamaParse
- Refer to the complete LlamaParse Documentation, fetching the `https://developers.llamaindex.ai/python/cloud/llamaparse/api-v2-guide/` page.

### Scripting Best Practices

Follow these guidelines when generating scripts:

#### 1. Always Use the Top-Level `LlamaCloud` Client

Use `LlamaCloud` (the API client) for all parsing operations:

```typescript
import LlamaCloud from "@llamaindex/llama-cloud";

// Define a client
const client = new LlamaCloud({
  apiKey: process.env["LLAMA_CLOUD_API_KEY"], // This is the default and can be omitted
});

```

#### 2. Two-Step Upload → Parse Pattern

Always upload first to get a file ID, then parse using the file ID. Never pass raw file bytes directly to `parse()`.

```typescript
import { readFile, writeFile } from "fs/promises";
import { basename } from "path";

// 1. Convert the file path into a File object
const buffer = await readFile(filePath);
const fileName = basename(filePath);
const file = new File([buffer], fileName);
// 2. Upload the file to the cloud
const fileObj = await client.files.create({
  file: file,
  purpose: "parse",
});
// 3. Get the file ID
const fileId = fileObj.id;
// 4. Use the file ID to parse the file
const result = await client.parsing.parse({
  tier: "agentic",
  version: "latest",
  file_id: fileId,
  ...
});
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
| `text_full` | Plain text via `result.text_full` |
| `markdown_full` | Markdown via `result.markdown_full` |
| `items` | Page-level JSON via `result.items.pages` |
| `text_content_metadata` | Per-page text metadata |
| `markdown_content_metadata` | Per-page markdown metadata |
| `items_content_metadata` | Per-page items metadata |
| `images_content_metadata` | Image list with presigned URLs |
| `output_pdf_content_metadata` | Output PDF metadata |
| `xlsx_content_metadata` | Excel-specific metadata |

Only request metadata `*_content_metadata` variants when you need presigned URLs or per-page detail — they increase payload size.

#### 5. Handle None Results Defensively

`result.text_full`, `result.markdown_full`, and `result.items` may be `undefined` on failure. Always guard against this:

```typescript
const text = result.text_full ?? "";
const markdown = result.markdown_full ?? "";
```

#### 6. Use Structured Options for Advanced Configuration

Group options using the correct nested keys:

```typescript
const result = await client.parsing.parse({
  tier: "agentic",
  version: "latest",
  file_id: fileId,
  input_options: {
    presentation: {
      skip_embedded_data: false,
    },
  },
  output_options: {
    images_to_save: ["screenshot"],
    markdown: {
      tables: { output_tables_as_markdown: true },
      annotate_links: true,
    },
  },
  processing_options: {
    specialized_chart_parsing: "agentic",
    ocr_parameters: { languages: ["de", "en"] },
  },
  agentic_options: {
    custom_prompt:
      "Extract text from the provided file and translate it from German to English.",
  },
  expand: [
    "markdown_full",
    "images_content_metadata",
    "markdown_content_metadata",
  ],
});
```

Use `agentic_options.custom_prompt` whenever the user wants to guide extraction (translation, summarization, structured extraction, etc.).

#### 7. Downloading Images Requires `httpx` and Auth

When `images_content_metadata` is in `expand`, download images via presigned URLs with Bearer auth:

```typescript
if (result.images_content_metadata) {
  for (const image of result.images_content_metadata.images) {
    if (image.presigned_url) {
      const response = await fetch(image.presigned_url, {
        headers: {
          Authorization: `Bearer ${process.env["LLAMA_CLOUD_API_KEY"]}`,
        },
      });
      if (response.ok) {
        const content = await response.bytes();
        await writeFile(image.filename, content);
      }
    }
  }
}
```

#### 8. Use the Node shebang

Every generated script should include the node shebang:

```typescript
#!/usr/bin/env node
```

---

## Step 2 — Execute the Typescript Script

Once the typescript script has been produced, you should:

1. Present the script to the user and ask for permissions to run it (depending on the current permissions settings)
2. Once you obtained permission to run, execute the script
3. Explore the results based on the user's requests

> In order to run typescript scripts, it is highly recommended to use: `npx tsx script.ts`.
