# leanblueprint_render — Agent Instructions

## What this tool does

Renders a **Lean blueprint dependency graph** from structured JSON. Takes a description of theorems/lemmas/definitions with their dependencies, generates LaTeX annotated with blueprint commands, and compiles to an interactive HTML site (with color-coded dependency graph) or PDF.

The output uses the plasTeX-based leanblueprint system: mathematical theorems appear as nodes, dependency arrows connect them, and node colors indicate formalization status.

## When to use this tool

Call `leanblueprint_render` when the user:
- Describes theorem dependencies and wants to **visualize** them
- Wants to create a **blueprint** for a Lean formalization project
- Asks to see how theorems relate to each other in a **dependency graph**
- Says "show me the dependency graph", "create a blueprint", "visualize theorems"

## How to translate user descriptions into the JSON

### Step 1: Identify all mathematical statements

Extract from the user's description:
- Theorems, lemmas, propositions, corollaries, definitions
- Assign each a unique `id` (snake_case, descriptive, e.g. `add_comm`, `zero_ne_succ`)

### Step 2: Determine types

| If the user says... | type |
|---------------------|------|
| "Theorem", "Thm" | `theorem` |
| "Lemma" | `lemma` |
| "Proposition", "Prop" | `proposition` |
| "Corollary", "Cor" | `corollary` |
| "Definition", "Def" | `definition` |

### Step 3: Extract dependencies

When the user says "X depends on Y" or "X uses Y", add Y's id to X's `uses` array.

When the user says "X is a corollary of Y", X depends on Y.

### Step 4: Determine status

| If the user says... | status |
|---------------------|--------|
| Has Lean code, "already formalized", "done" | `stated` |
| "Not yet", "todo", "work in progress", WIP | `not_ready` |
| "In Mathlib", "already in mathlib4" | `mathlib` |

When no status is specified, default to `not_ready`.

### Step 5: Format the statement

Write the mathematical statement using **LaTeX math notation**:
- Inline math: `$a + b = b + a$`
- Display math: `$$\sum_{i=1}^n i = \frac{n(n+1)}{2}$$`
- Use proper LaTeX commands: `\forall`, `\exists`, `\implies`, `\iff`, `\mathbb{N}`, `\mathrm{succ}`

### Step 6: Group into chapters

If the user describes logical groupings, create separate chapters. Otherwise, put everything in one chapter (e.g., "Results").

### Step 7: Lean declarations (optional)

If the user mentions Lean code files or declaration names, include them in `lean_decls`. Format: `["ProjectName.declName"]`.

## Example

**User says:** "Define natural numbers. Then prove zero is not the successor of any natural number. Finally, state (but don't prove) that addition is commutative. Commutativity depends on the definition of naturals. The zero-is-not-successor lemma also depends on the natural numbers definition."

**You call leanblueprint_render with:**

```json
{
  "title": "Natural Numbers",
  "author": "User",
  "format": "html",
  "chapters": [
    {
      "name": "Basic Properties",
      "items": [
        {
          "id": "nat",
          "type": "definition",
          "name": "Natural Numbers",
          "statement": "The type of natural numbers $\\mathbb{N}$ is defined as an inductive type with constructors $0 : \\mathbb{N}$ and $\\mathrm{succ} : \\mathbb{N} \\to \\mathbb{N}$.",
          "status": "stated",
          "lean_decls": ["Nat"]
        },
        {
          "id": "zero_ne_succ",
          "type": "lemma",
          "name": "Zero is not a successor",
          "statement": "For any natural number $n$, $0 \\neq \\mathrm{succ}(n)$.",
          "uses": ["nat"],
          "status": "stated",
          "proof": "By the no-confusion property of inductive types.",
          "lean_decls": ["Nat.succ_ne_zero"]
        },
        {
          "id": "add_comm",
          "type": "theorem",
          "name": "Addition is commutative",
          "statement": "For all natural numbers $a$ and $b$, $a + b = b + a$.",
          "uses": ["nat"],
          "status": "not_ready"
        }
      ]
    }
  ]
}
```

## Color scheme in the output

| Border | Fill | Meaning |
|--------|------|---------|
| Dark green | — | Already in Mathlib |
| Green | — | Statement formalized |
| Blue | — | Ready to formalize (deps done) |
| Orange | — | Not ready |
| — | Dark green | Fully proved (ancestors all done) |

## Errors

If the build fails, read the error output — it usually points to a LaTeX syntax error in the `statement` or `proof` fields. Common issues:
- Unescaped special characters like `%`, `&`, `_` outside math mode
- Missing `$` around math expressions
- Unmatched braces

## Dependency errors

If the tool reports missing Python packages, tell the user to run:

```bash
pip install plastex plastexdepgraph leanblueprint
```

These are required for LaTeX → HTML compilation. The user needs Python 3.7+ installed first.

For `lake build` failures (when `lean_build: true`), the user needs Lean 4 installed via `elan`:
https://lean-lang.org/lean4/doc/setup.html

## Generating Lean 4 code

When the user wants Lean 4 source code (`.lean` files), include the `lean` field in each item. Set `generate_lean: true` in the top-level input. Optionally set `lean_build: true` to also compile with `lake build`.

### The `lean` field

```json
{
  "lean": {
    "module": "MyProject.Basic",
    "decl": "theorem add_comm (a b : Nat) : a + b = b + a := by\n  induction a with\n  | zero => simp\n  | succ a ih => simp [ih]"
  }
}
```

- `module`: The Lean module path (optional). Defaults to `<ProjectName>.<ChapterName>` derived from the chapter. Use PascalCase, e.g. `MyProject.DifferentialCalculus`.
- `decl`: The **complete** Lean 4 declaration including keyword, name, type signature, and proof. Use `:= by` for tactic proofs, `:=` for term proofs.

### Lean 4 syntax quick reference

```
theorem name (args : Types) : ReturnType := by
  tactic1
  tactic2

lemma name (args : Types) : ReturnType := by
  ...

def name (args : Types) : ReturnType :=
  term
```

Common tactics: `intro`, `apply`, `exact`, `have`, `rw`, `simp`, `induction`, `cases`, `ring`, `positivity`, `omega`.

### `lean_decls` auto-derivation

When `generate_lean: true`, the tool automatically fills `lean_decls` from the `lean.decl` field. For example, if `module` is `MyProject.Basic` and `decl` starts with `theorem add_comm`, the derived lean_decl is `MyProject.Basic.add_comm`. You do NOT need to manually set `lean_decls` when `lean.decl` is provided.

### Cross-module dependencies

If an item in Chapter A depends on (`uses`) an item in Chapter B, the generated Lean file for Chapter A will automatically import Chapter B's module. No manual import management needed.

### Example with Lean code

```json
{
  "title": "Calculus",
  "generate_lean": true,
  "lean_build": true,
  "chapters": [
    {
      "name": "DifferentialCalculus",
      "items": [
        {
          "id": "rolle",
          "type": "theorem",
          "statement": "If $f \\in C[a,b]$, $f$ differentiable on $(a,b)$, and $f(a)=f(b)$, then $\\exists\\,c\\in(a,b),\\; f'(c)=0$.",
          "uses": [],
          "status": "stated",
          "lean": {
            "decl": "theorem rolle (f : ℝ → ℝ) (hcont : ContinuousOn f (Set.Icc a b)) (hdiff : DifferentiableOn ℝ f (Set.Ioo a b)) (heq : f a = f b) : ∃ c ∈ Set.Ioo a b, deriv f c = 0 := by\n  sorry"
          }
        }
      ]
    }
  ]
}
```
