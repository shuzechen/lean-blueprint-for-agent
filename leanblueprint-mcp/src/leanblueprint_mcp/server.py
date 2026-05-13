"""MCP server for leanblueprint — render Lean 4 blueprint dependency graphs."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationCapabilities
from mcp.server.stdio import stdio_server
import mcp.types as types

from .schema import BlueprintInput
from .generator import scaffold, generate_content
from .lean_gen import generate_lean_files, fill_lean_decls, _to_lean_pkg_name
from .build import check_dependencies, build_web, build_lean

server = Server("leanblueprint")

DESCRIPTION = """Render a Lean blueprint dependency graph from structured theorem data.

This tool converts a JSON description of mathematical theorems, their proofs, and
interdependencies into a color-coded interactive HTML dependency graph (or PDF) using
the Lean blueprint system. It can also generate Lean 4 source code files.

The input describes chapters containing items (theorems, lemmas, propositions,
corollaries, definitions) with:
- A unique id for each item
- The type of statement
- The mathematical statement itself (in LaTeX)
- Dependencies (uses) on other items by their ids
- Formalization status (stated, not_ready, mathlib)
- Optional Lean declaration names (auto-derived from lean.decl if generate_lean=true)
- Optional proof text
- Optional Lean 4 code (lean.decl) for generating .lean source files

Output is placed in blueprint/web/ (HTML) relative to the project directory.
Lean files are placed in <ProjectName>/ (e.g. MyProject/Basic.lean)."""

INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Project title"},
        "author": {"type": "string", "description": "Author name"},
        "home": {"type": "string", "description": "Project website URL"},
        "github": {"type": "string", "description": "GitHub repository URL"},
        "dochome": {"type": "string", "description": "API documentation base URL"},
        "format": {
            "type": "string",
            "enum": ["html", "pdf"],
            "default": "html",
            "description": "Output format",
        },
        "generate_lean": {
            "type": "boolean",
            "default": False,
            "description": "Also generate Lean 4 .lean source files",
        },
        "lean_build": {
            "type": "boolean",
            "default": False,
            "description": "Run 'lake build' after generating Lean files",
        },
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
                                    "description": "Unique identifier, e.g. 'add_comm'",
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
                                    "description": "Statement in LaTeX math, e.g. '$a+b=b+a$'",
                                },
                                "uses": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "IDs of items this depends on",
                                },
                                "lean_decls": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Lean declaration names. Auto-derived from lean.decl if omitted.",
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
                                        "module": {
                                            "type": "string",
                                            "description": "Lean module path, e.g. 'MyProject.Basic'",
                                        },
                                        "decl": {
                                            "type": "string",
                                            "description": "Full Lean 4 declaration with proof",
                                        },
                                    },
                                    "required": ["decl"],
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

    # Check Python dependencies
    dep_errors = check_dependencies()
    if dep_errors:
        return [types.TextContent(
            type="text",
            text="Blueprint setup failed:\n\n" + "\n".join(f"- {e}" for e in dep_errors),
        )]

    # Determine project directory
    project_dir = Path(os.getenv("LEANBLUEPRINT_PROJECT", ".")).resolve()
    src_dir = project_dir / "blueprint" / "src"
    already_existed = src_dir.exists()

    # Scaffold blueprint files
    scaffold(src_dir, inp)

    # Generate Lean 4 files if requested
    lean_modules: list[str] = []
    if inp.generate_lean:
        fill_lean_decls(inp.chapters, _to_lean_pkg_name(inp.title))
        lean_modules = generate_lean_files(project_dir, inp)

        # Update content.tex with auto-derived lean_decls
        content_path = src_dir / "content.tex"
        content_path.write_text(generate_content(inp), encoding="utf-8")

        if inp.lean_build:
            lb = build_lean(project_dir)
            if not lb.success:
                msg = f"Lean 4 build (lake build) failed.\n\n{lb.stderr or lb.stdout}"
                return [types.TextContent(type="text", text=msg)]

    # Build blueprint HTML/PDF
    fmt = inp.format or "html"
    build_result = build_web(project_dir)

    if not build_result.success:
        msg = f"Blueprint build failed.\n\n{build_result.stderr or build_result.stdout}"
        return [types.TextContent(type="text", text=msg)]

    chapter_count = len(inp.chapters)
    item_count = sum(len(ch.items) for ch in inp.chapters)
    action = "Updated" if already_existed else "Created"

    msg = f"{action} blueprint with {chapter_count} chapter(s) and {item_count} item(s).\n\n"
    msg += f"Output ({fmt}): {build_result.output_path}\n\n"
    msg += "Open blueprint/web/index.html in a browser to view the dependency graph."

    if lean_modules:
        msg += f"\n\nLean 4 source files generated:\n  Directory: {project_dir / _to_lean_pkg_name(inp.title)}"
        msg += f"\n  Modules: {', '.join(lean_modules)}"

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
