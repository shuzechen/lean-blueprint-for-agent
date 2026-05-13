"""JSON → Lean 4 source files generator."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from .schema import BlueprintInput, Chapter


def _to_lean_pkg_name(title: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff\s]", "", title)
    name = re.sub(r"\s+", "", name)
    if not name or name[0].isdigit():
        name = "MyProject"
    return name


def _chapter_to_module(project_name: str, chapter: Chapter) -> str:
    suffix = re.sub(r"[^\w\u4e00-\u9fff]", "", chapter.name)
    suffix = re.sub(r"^\d+", "", suffix)
    return f"{project_name}.{suffix or 'Chapter'}"


def parse_decl_name(decl: str) -> str | None:
    m = re.match(r"^\s*(?:theorem|lemma|def|example)\s+(\w[\w']*)", decl)
    return m.group(1) if m else None


def derive_lean_decl(module: str, decl: str) -> str | None:
    name = parse_decl_name(decl)
    return f"{module}.{name}" if name else None


def collect_lean_decls(chapters: list[Chapter], project_name: str) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for ch in chapters:
        module = _chapter_to_module(project_name, ch)
        for item in ch.items:
            if not item.lean or not item.lean.decl:
                continue
            full = derive_lean_decl(module, item.lean.decl)
            if full:
                mapping.setdefault(item.id, []).append(full)
    return mapping


def fill_lean_decls(chapters: list[Chapter], project_name: str) -> None:
    decl_map = collect_lean_decls(chapters, project_name)
    for ch in chapters:
        for item in ch.items:
            if item.lean_decls:
                continue
            derived = decl_map.get(item.id)
            if derived:
                item.lean_decls = derived


def _gather_imports(chapters: list[Chapter], project_name: str) -> dict[str, list[str]]:
    mod_imports: dict[str, set[str]] = {}
    all_ids: dict[str, str] = {}
    for ch in chapters:
        module = _chapter_to_module(project_name, ch)
        for item in ch.items:
            all_ids[item.id] = module

    for ch in chapters:
        module = _chapter_to_module(project_name, ch)
        imports = mod_imports.setdefault(module, set())
        for item in ch.items:
            if not item.uses:
                continue
            for dep_id in item.uses:
                dep_mod = all_ids.get(dep_id)
                if dep_mod and dep_mod != module:
                    imports.add(dep_mod)

    return {k: sorted(v) for k, v in mod_imports.items()}


def _detect_lean_version() -> str | None:
    try:
        out = subprocess.run(
            ["lean", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        m = re.search(r"version (\d+\.\d+\.\d+)", out.stdout)
        if m:
            return f"leanprover/lean4:v{m.group(1)}"
    except Exception:
        pass
    return None


def generate_lean_files(root_dir: Path, inp: BlueprintInput) -> list[str]:
    project_name = _to_lean_pkg_name(inp.title)
    lean_dir = root_dir / project_name
    lean_dir.mkdir(parents=True, exist_ok=True)

    fill_lean_decls(inp.chapters, project_name)
    module_imports = _gather_imports(inp.chapters, project_name)
    modules: list[str] = []

    for ch in inp.chapters:
        has_lean = any(item.lean and item.lean.decl for item in ch.items)
        if not has_lean:
            continue

        module_name = _chapter_to_module(project_name, ch)
        short_name = module_name[len(project_name) + 1:]
        file_path = lean_dir / f"{short_name}.lean"

        imports = module_imports.get(module_name, [])
        lines: list[str] = []
        for imp in imports:
            lines.append(f"import {imp}")
        if imports:
            lines.append("")

        for item in ch.items:
            if not item.lean or not item.lean.decl:
                continue
            lines.append(item.lean.decl.strip())
            lines.append("")

        file_path.write_text("\n".join(lines), encoding="utf-8")
        modules.append(module_name)

    if modules:
        root_content = "\n".join(
            f"import {project_name}.{m[len(project_name) + 1:]}"
            for m in modules
        ) + "\n"
        (lean_dir / f"{project_name}.lean").write_text(root_content, encoding="utf-8")

    lakefile = root_dir / "lakefile.lean"
    if not lakefile.exists():
        lf_content = f"""import Lake
open Lake DSL

package «{project_name}» where

@[default_target]
lean_lib {project_name} where
"""
        lakefile.write_text(lf_content, encoding="utf-8")

    toolchain_file = root_dir / "lean-toolchain"
    if not toolchain_file.exists():
        ver = _detect_lean_version()
        if ver:
            toolchain_file.write_text(ver, encoding="utf-8")

    return modules
