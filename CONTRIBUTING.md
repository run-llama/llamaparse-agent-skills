# Contributing to LlamaParse Skills

Thank you for your interest in contributing to this project! Please review these guidelines before getting started.

## Issue Reporting

### When to Report an Issue

- You've discovered bugs but lack the knowledge or time to fix them
- You have feature requests but cannot implement them yourself

> ⚠️ **Important:** Always search existing open and closed issues before submitting to avoid duplicates.

### How to Report an Issue

1. Open a new issue
2. Provide a clear, concise title that describes the problem or feature request
3. Include a detailed description of the issue or requested feature

## Code Contributions

### When to Contribute

- You've identified and fixed bugs
- You've optimized or improved existing code
- You've developed new features that would benefit the community

### How to Contribute

> [uv](https://docs.astral.sh/uv) is required for contributions.

1. **Fork the repository and check out a secondary branch**

2. **Ensure frontmatter is correctly formatted across all skills**
  ```bash
  cd scripts/
  ./ensure_frontmatter.py
  ```  

3. **If you created a new skill, make sure to add metadata in [`metadata.json`](./metadata.json)**:

  ```json
  {
    "my-skill": {
      "version": "0.1.0",
      "author": "LlamaIndex"
    }
  }
  ```
  To do so, run:
  
  ```bash
  cd scripts/
  ./add_skill.py my-skill # defaults to 'LlamaIndex' as author and '0.1.0' as version
  ./add_skill.py my-skill --author "LlamaIndex and Acme Inc" --version 0.0.0
  ```

5. **Commit your changes**

6. **Submit a pull request**
   Include a comprehensive description of your changes.

### How to Release (maintainers only)

Once changes are merged, you can run the `Pre-release for skill` GitHub Action through manual dispatch, updating the version of a specific skill according to SemVer conventions.

This will generate a release PR with the updated version in [`metadata.json`](./metadata.json) and in the frontmatter of the `SKILL.md` file of the skill whose release you prepared.

---

**Thank you for contributing!**
