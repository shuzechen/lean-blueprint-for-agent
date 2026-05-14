"""MCP server for leanblueprint — render Lean 4 blueprint dependency graphs."""

from __future__ import annotations

import os
from pathlib import Path

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationCapabilities
from mcp.server.stdio import stdio_server
import mcp.types as types

from .schema import BlueprintInput
from .generator import scaffold, generate_content, write_lean_sources_sidecar
from .build import check_dependencies, build_web

server = Server("leanblueprint")

DESCRIPTION = """Render a Lean blueprint dependency graph from a structured theorem description.

The agent passes a JSON description of chapters and items (theorems, lemmas,
propositions, corollaries, definitions). Each item has a unique id, the
mathematical statement in LaTeX, its dependencies (uses) on other items by id,
a formalization status, and — for items backed by Lean code the agent has
already written — a reference to the Lean source file at `lean.file`.

The MCP scaffolds blueprint/src/ and renders an interactive HTML dependency
graph in blueprint/web/. For every item whose `lean.file` is set, the MCP
reads that file from disk and embeds its imports + body in the L∃∀N modal
that opens when a graph node is clicked. The MCP does not compile Lean and
does not produce any external doc-gen links — the modal is fully self-contained.

The project directory the blueprint is rendered into is `$LEANBLUEPRINT_PROJECT`
(or the current working directory if unset). All `lean.file` paths are
interpreted relative to that directory."""

INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Project title"},
        "author": {"type": "string", "description": "Author name"},
        "home": {"type": "string", "description": "Project website URL"},
        "github": {"type": "string", "description": "GitHub repository URL"},
        "chapters": {
            "type": "array",
            "description": "Theorem chapters",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Chapter name"},
                    "items": {
                        "type": "array",
                        "description": "Items in this chapter",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "string",
                                    "description": "Unique identifier, e.g. 'dmc'",
                                },
                                "type": {
                                    "type": "string",
                                    "enum": ["theorem", "lemma", "proposition", "corollary", "definition"],
                                    "description": "Type of statement",
                                },
                                "name": {
                                    "type": "string",
                                    "description": "Display title",
                                },
                                "statement": {
                                    "type": "string",
                                    "description": "Statement in LaTeX, e.g. '$a+b=b+a$'",
                                },
                                "uses": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "IDs of items this depends on",
                                },
                                "status": {
                                    "type": "string",
                                    "enum": ["stated", "not_ready", "mathlib"],
                                    "description": "Formalization status: stated=formalized, not_ready=todo, mathlib=in Mathlib",
                                },
                                "proof": {
                                    "type": "string",
                                    "description": "Proof text in LaTeX",
                                },
                                "discussion": {
                                    "type": "integer",
                                    "description": "GitHub issue number for discussion",
                                },
                                "lean": {
                                    "type": "object",
                                    "properties": {
                                        "file": {
                                            "type": "string",
                                            "description": "Lean source file path, relative to the project directory, e.g. 'Definitions/Def_DMC.lean'",
                                        },
                                    },
                                    "required": ["file"],
                                },
                            },
                            "required": ["id", "type", "statement", "status"],
                        },
                    },
                },
                "required": ["name", "items"],
            },
        },
    },
    "required": ["title", "chapters"],
}


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="leanblueprint_render",
            description=DESCRIPTION,
            inputSchema=INPUT_SCHEMA,
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name != "leanblueprint_render":
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

    try:
        inp = BlueprintInput.model_validate(arguments)
    except Exception as e:
        return [types.TextContent(type="text", text=f"Invalid input: {e}")]

    dep_errors = check_dependencies()
    if dep_errors:
        return [types.TextContent(
            type="text",
            text="Blueprint setup failed:\n\n" + "\n".join(f"- {e}" for e in dep_errors),
        )]

    project_dir = Path(os.getenv("LEANBLUEPRINT_PROJECT", ".")).resolve()
    src_dir = project_dir / "blueprint" / "src"
    already_existed = src_dir.exists()

    scaffold(src_dir, inp)
    sidecar_counts = write_lean_sources_sidecar(project_dir, inp)

    build_result = build_web(project_dir)
    if not build_result.success:
        msg = f"Blueprint build failed.\n\n{build_result.stderr or build_result.stdout}"
        return [types.TextContent(type="text", text=msg)]

    chapter_count = len(inp.chapters)
    item_count = sum(len(ch.items) for ch in inp.chapters)
    action = "Updated" if already_existed else "Created"

    msg = (
        f"{action} blueprint with {chapter_count} chapter(s) and {item_count} item(s).\n\n"
        f"Output (html): {build_result.output_path}\n"
        f"Lean source files embedded in modal: {sidecar_counts['included']} "
        f"(missing on disk: {sidecar_counts['missing']})\n\n"
        f"Open blueprint/web/index.html in a browser to view the dependency graph."
    )
    return [types.TextContent(type="text", text=msg)]


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationCapabilities(
                sampling={},
                experimental={},
            ),
        )


def cli() -> None:
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    cli()
