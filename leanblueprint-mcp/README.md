# leanblueprint-mcp

MCP server for rendering Lean 4 blueprint dependency graphs from structured theorem data.

Works with any MCP-compatible client (Claude Desktop, Cursor, VS Code, Continue, etc.).

## Install

```bash
pip install leanblueprint-mcp
```

Or from source:

```bash
pip install -e .
```

## Prerequisites

```bash
pip install plastex plastexdepgraph leanblueprint
```

| Package | Purpose |
|---------|---------|
| Python 3.10+ | Runtime |
| `plastex` | LaTeX → HTML compiler |
| `plastexdepgraph` | Dependency graph generation (DOT → d3-graphviz) |
| `leanblueprint` | Blueprint LaTeX macros, CSS, Lean declaration tracking |

Optional:

| Dependency | Purpose | Install |
|-----------|---------|---------|
| Lean 4 (`elan`) | `.lean` code generation + `lake build` | https://lean-lang.org/lean4/doc/setup.html |

## MCP Client Configuration

### Claude Desktop

```json
{
  "mcpServers": {
    "leanblueprint": {
      "command": "python",
      "args": ["-m", "leanblueprint_mcp.server"]
    }
  }
}
```

### Codex / Cursor / Continue

```json
{
  "mcpServers": {
    "leanblueprint": {
      "command": "leanblueprint-mcp"
    }
  }
}
```

## Tools

### `leanblueprint_render`

Takes a JSON description of mathematical theorems, their proofs, and interdependencies, and compiles them into a color-coded interactive HTML dependency graph.

See `AGENTS.md` for the full input schema and usage examples for LLM agents.

## License

MIT
