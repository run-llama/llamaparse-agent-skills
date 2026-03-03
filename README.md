# LlamaParse Skills

Unblock document intelligence for your agents with LlamaParse skills.

## Available Skills

### llamaparse 

Unstructured documents parsing and text-extraction guidelines leveraging LlamaParse.

**Use with:**

- PDFs, presentations, Word documents, spreadsheets, images
- Complex documents which need advanced parsing capabilties in order to get their content extracted
- Documents with images, charts and tables
- In general, whenever the agent needs to have access to a deeper layer than just raw text extraction

**Pre-requisites**

- A `LLAMA_CLOUD_API_KEY` available within the environment
- Node 18+ and `npm` (or another package manager)
- (Optional) `@llamaindex/llama-cloud@latest` typescript package installed in the current Node environment


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
