# LlamaParse Skills

Unblock document intelligence for your agents with LlamaParse skills.

## Available Skills

### llamaparse 

Skill for unstructured documents parsing and text-extraction leveraging LlamaParse.

**Use with:**

- PDFs, presentations, Word documents, spreadsheets, images
- Complex documents which need advanced parsing capabilties in order to get their content extracted
- Documents with images, charts and tables
- In general, whenever the agent needs to have access to a deeper layer than just raw text extraction

**Pre-requisites**

- A `LLAMA_CLOUD_API_KEY` available within the environment
- Node 18+ and `npm` (or another package manager)
- (Optional) `@llamaindex/llama-cloud@latest` typescript package installed in the current Node environment

### liteparse

Skill for local-first, fast document parsing, conversion and spatial text extraction.

**Use with:**

- PDFs (main target), Office documents and images (require extra dependencies)
- Text-dense documents with tables and images
- In general, whenever the agent needs a quick and not-100%-accurate way to extract content from unstructured documents

**Pre-requisites**

- Node 18+ and `npm` (or another package manager)
- `@llamaindex/liteparse` globally installed (`npm install -g @llamaindex/liteparse`)
- (Optional) Libreoffice for Office documents support
- (Optional) Imagemagick for images support

### llamacloud-index

Skill for agentic retrieval over LlamaCloud Index v2, the managed knowledge base of the LlamaParse Platform, through the platform REST API with `curl`.

**Use with:**

- Questions that should be answered from documents stored in an Index v2 knowledge base
- Agentic retrieval workflows: discover indexes, locate files, grep indexed content, and retrieve passages with hybrid (sparse + dense) search
- In general, whenever the agent should navigate an index like a file system instead of doing one-shot RAG

**Pre-requisites**

- A `LLAMA_CLOUD_API_KEY` available within the environment
- `curl` (and, recommended, `jq`)
- An existing [Index v2](https://developers.llamaindex.ai/llamaparse/cloud-index-v2/getting_started/) index

## Installation

With the `skills` CLI:

```bash
npx skills add run-llama/llamaparse-agent-skills
```

Or, if you wish to download only one skill:

```bash
npx skills add run-llama/llamaparse-agent-skills --skill llamaparse # or the name of another skill
```

You can also download the skills folder in `.zip` format from [GitHub Releases](https://github.com/run-llama/llamaparse-agent-skills/releases/download/latest/skills-latest.zip).

## License 

[MIT](./LICENSE)
