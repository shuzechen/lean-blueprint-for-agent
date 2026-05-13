"""Pydantic models for leanblueprint rendering input."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ItemType(str, Enum):
    theorem = "theorem"
    lemma = "lemma"
    proposition = "proposition"
    corollary = "corollary"
    definition = "definition"


class ItemStatus(str, Enum):
    stated = "stated"
    not_ready = "not_ready"
    mathlib = "mathlib"


class LeanCode(BaseModel):
    module: Optional[str] = Field(
        None,
        description="Lean module path, e.g. 'MyProject.Basic'. Defaults to derived from chapter name.",
    )
    decl: str = Field(
        ...,
        description=(
            "Full Lean 4 declaration: keyword, name, type signature, and proof. "
            "E.g. 'theorem add_comm (a b : Nat) : a + b = b + a := by\\n  induction a ...'"
        ),
    )


class BlueprintItem(BaseModel):
    id: str = Field(..., description="Unique identifier, e.g. 'add_comm'")
    type: ItemType = Field(..., description="Type of mathematical statement")
    name: Optional[str] = Field(None, description="Display title")
    statement: str = Field(..., description="Statement in LaTeX math, e.g. '$a+b=b+a$'")
    uses: Optional[list[str]] = Field(None, description="IDs of items this depends on")
    lean_decls: Optional[list[str]] = Field(
        None,
        description="Lean declaration names. Auto-derived from lean.decl when generate_lean=true.",
    )
    status: ItemStatus = Field(
        ...,
        description="Formalization status: stated=formalized, not_ready=todo, mathlib=in Mathlib",
    )
    proof: Optional[str] = Field(None, description="Proof text in LaTeX")
    discussion: Optional[int] = Field(None, description="GitHub issue number for discussion")
    lean: Optional[LeanCode] = Field(
        None,
        description="Lean 4 source code for this item. When provided, generates .lean files.",
    )


class Chapter(BaseModel):
    name: str = Field(..., description="Chapter name")
    items: list[BlueprintItem] = Field(..., description="Items in this chapter")


class BlueprintInput(BaseModel):
    title: str = Field(..., description="Project title")
    author: Optional[str] = Field(None, description="Author name")
    home: Optional[str] = Field(None, description="Project website URL")
    github: Optional[str] = Field(None, description="GitHub repository URL")
    dochome: Optional[str] = Field(
        None,
        description="API documentation base URL",
    )
    format: str = Field(default="html", description="Output format: 'html' or 'pdf'")
    generate_lean: bool = Field(
        default=False,
        description="Also generate Lean 4 .lean source files from lean.decl fields",
    )
    lean_build: bool = Field(
        default=False,
        description="Run 'lake build' after generating Lean files",
    )
    chapters: list[Chapter] = Field(..., description="Theorem chapters")
