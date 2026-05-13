"""Build runner — plasTeX compilation and lake build."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BuildResult:
    success: bool
    output_path: str
    stdout: str
    stderr: str


def check_dependencies() -> list[str]:
    errors: list[str] = []

    try:
        subprocess.run(["python", "--version"], capture_output=True, timeout=5)
    except Exception:
        errors.append("Python 3.7+ is required. Install from https://python.org")
        return errors

    for mod, name in [
        ("plasTeX", "plasTeX"),
        ("plastexdepgraph", "plastexdepgraph"),
        ("leanblueprint", "leanblueprint"),
    ]:
        try:
            subprocess.run(
                ["python", "-c", f"import {mod}"],
                capture_output=True,
                timeout=10,
                check=True,
            )
        except Exception:
            errors.append(f"{name} is not installed. Run: pip install {name}")

    return errors


def build_web(root_dir: Path) -> BuildResult:
    src_dir = root_dir / "blueprint" / "src"

    try:
        result = subprocess.run(
            ["plastex", "-c", "plastex.cfg", "web.tex"],
            cwd=str(src_dir),
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ, "PYTHONUTF8": "1"},
        )
        return BuildResult(
            success=result.returncode == 0,
            output_path=str(root_dir / "blueprint" / "web"),
            stdout=result.stdout,
            stderr=result.stderr,
        )
    except subprocess.TimeoutExpired:
        return BuildResult(
            success=False,
            output_path=str(root_dir / "blueprint" / "web"),
            stdout="",
            stderr="plasTeX compilation timed out (120s)",
        )
    except Exception as e:
        return BuildResult(
            success=False,
            output_path=str(root_dir / "blueprint" / "web"),
            stdout="",
            stderr=str(e),
        )


def build_lean(root_dir: Path) -> BuildResult:
    try:
        result = subprocess.run(
            ["lake", "build"],
            cwd=str(root_dir),
            capture_output=True,
            text=True,
            timeout=300,
        )
        return BuildResult(
            success=result.returncode == 0,
            output_path=str(root_dir),
            stdout=result.stdout,
            stderr=result.stderr,
        )
    except subprocess.TimeoutExpired:
        return BuildResult(
            success=False,
            output_path=str(root_dir),
            stdout="",
            stderr="lake build timed out (300s)",
        )
    except FileNotFoundError:
        return BuildResult(
            success=False,
            output_path=str(root_dir),
            stdout="",
            stderr="Lean 4 (lake) not found. Install via: https://lean-lang.org/lean4/doc/setup.html",
        )
    except Exception as e:
        return BuildResult(
            success=False,
            output_path=str(root_dir),
            stdout="",
            stderr=str(e),
        )
