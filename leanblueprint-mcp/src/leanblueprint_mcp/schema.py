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
    file: str = Field(
        ...,
        description=(
            "Path to the Lean source file for this blueprint item, relative to "
            "the project directory the MCP renders into. One blueprint item "
            "maps to one Lean file; the MCP reads the file at render time and "
            "embeds its imports + body in the L∃∀N modal. Example: "
            "'Definitions/Def_DMC.lean'."
        ),
    )


class BlueprintItem(BaseModel):
    id: str = Field(..., description="Unique identifier, e.g. 'add_comm'")
    type: ItemType = Field(..., description="Type of mathematical statement")
    name: Optional[str] = Field(None, description="Display title")
    statement: str = Field(..., description="Statement in LaTeX math, e.g. '$a+b=b+a$'")
    uses: Optional[list[str]] = Field(None, description="IDs of items this depends on")
    status: ItemStatus = Field(
        ...,
        description="Formalization status: stated=formalized, not_ready=todo, mathlib=in Mathlib",
    )
    proof: Optional[str] = Field(None, description="Proof text in LaTeX")
    discussion: Optional[int] = Field(None, description="GitHub issue number for discussion")
    lean: Optional[LeanCode] = Field(
        None,
        description=(
            "Reference to the Lean source file for this item. When provided, "
            "the file is read and its contents are shown in the L∃∀N modal."
        ),
    )


class Chapter(BaseModel):
    name: str = Field(..., description="Chapter name")
    items: list[BlueprintItem] = Field(..., description="Items in this chapter")


class BlueprintInput(BaseModel):
    title: str = Field(..., description="Project title")
    author: Optional[str] = Field(None, description="Author name")
    home: Optional[str] = Field(None, description="Project website URL")
    github: Optional[str] = Field(None, description="GitHub repository URL")
    chapters: list[Chapter] = Field(..., description="Theorem chapters")
