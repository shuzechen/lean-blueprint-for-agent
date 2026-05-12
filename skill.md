---
name: lean-blueprint
description: Take a mathematician's informal description of a target theorem and its proof decomposition, then produce (a) Lean 4 statements with `sorry` placeholders for every theorem and lemma, (b) a matching LaTeX blueprint that explains each step in prose, and (c) a built blueprint site (HTML + PDF + dependency graph) the mathematician can review. Use this skill whenever the user wants to "blueprint" a proof, formalize a paper, or scaffold the Lean side of a formalization project from an informal sketch.
---

# Lean Blueprint authoring skill

You are formalizing mathematics on behalf of a human mathematician. The mathematician describes a theorem and a proof decomposition in prose; your job is to turn that into (1) Lean 4 statements they can audit, (2) a LaTeX blueprint that re-states the same content in human-readable form with a dependency graph, and (3) a built blueprint site.

The Lean is for the mathematician to **check** — write statements, leave proofs as `sorry`. The LaTeX is for the mathematician to **understand** what you intend to prove and how the pieces fit. The blueprint is the deliverable that ties the two together with hyperlinks and a dependency graph.

## 0. Preconditions you must verify

Before doing anything else:

- The current working directory contains a Lean 4 project, i.e. a `lakefile.lean` **or** a `lakefile.toml` at the repo root. (Both flavors are supported; if both files exist, `lakefile.lean` takes precedence.) If neither exists, stop and ask the mathematician where their Lean project lives — `cd` into it. **Do not invent a Lean project.**
- The working tree is clean (`git status` shows no uncommitted changes). `leanblueprint new` refuses to run otherwise. If it's dirty, ask the user to commit or stash first.
- There is no existing `blueprint/` directory. If there is one, you are extending an existing blueprint — skip step 2 (scaffolding) and only add new content in `blueprint/src/content.tex`.

## 1. Install the `leanblueprint` tool

Graphviz is a system dependency of `plastexdepgraph` and must already be installed (`graphviz` and `libgraphviz-dev` / `graphviz-dev` on Linux, `brew install graphviz` on macOS). If `pygraphviz` fails to build during the steps below, surface the error to the user — do not silently skip.

Preferred (from PyPI):

```bash
pip install leanblueprint
which leanblueprint            # sanity check
```

If the mathematician needs a feature that isn't in the released version yet, or asked you to use a fork, clone and install from source instead:

```bash
# from a workspace directory, not inside the Lean project
git clone https://github.com/PatrickMassot/leanblueprint.git
cd leanblueprint
pip install .
cd -                           # back to the Lean project
which leanblueprint
```

Use the default branch — do **not** check out the old `client` branch. It existed as a staging branch while the CLI was being built and has been superseded by `master`; pinning to `@client` will give you a March-2024 snapshot missing `lakefile.toml` support, the Jekyll home page, the doc-gen prompt, and several bug fixes.

If `leanblueprint` is already on PATH, skip the install.

## 2. Understand the mathematician's request

The mathematician will describe their goal in prose — possibly in chat, possibly in a paper, possibly mid-conversation. Before writing any Lean or LaTeX, you must extract:

1. **The target theorem.** Its statement, in mathematical English. If the mathematician gave you a paper or a sketch, pull the exact statement; do not paraphrase loosely.
2. **The proof decomposition.** The list of intermediate lemmas (and their statements) plus how they combine to prove the target. This is the most important thing to get right — it determines the blueprint's dependency graph.
3. **Definitions.** Every non-standard object that appears in any statement. A definition node in the blueprint is different from a theorem node — see §6 on `\leanok` semantics.
4. **Existing formalization.** Which lemmas (if any) are already in the project, in Mathlib, or in another dependency. Do not redefine them; reference them.
5. **The Lean library name.** Read `lakefile.lean` for `lean_lib` entries. If there are several, ask which one to extend.

**Ask before assuming.** If the mathematician's sketch is missing a step, name the gap explicitly and ask — do not paper over it with a "clearly" in the LaTeX or a `sorry` in the Lean without flagging it. A blueprint whose graph is wrong is worse than no blueprint, because it gives a false picture of what is left to do.

When you've extracted the structure, **write it back to the mathematician as a numbered list of statements and dependencies and get explicit confirmation before generating anything.** This is your last cheap chance to catch a misread.

## 3. Scaffold the blueprint

From inside the Lean project root:

```bash
leanblueprint new
```

This is interactive. Accept defaults unless the mathematician has given you a reason to override (project title, author, document class, etc.). It will:

- create `blueprint/src/` populated from Jinja2 templates,
- offer to edit the lakefile (`lakefile.lean` or `lakefile.toml` — both supported) to add the `checkdecls` requirement and run `lake update checkdecls`. **Accept this; the verification step in §6 depends on it.**
- offer to edit the lakefile to add `doc-gen4` and run `lake -R -Kenv=dev update doc-gen4`. Accept this unless the mathematician explicitly doesn't want API docs.
- offer to scaffold a Jekyll **home page** at `home_page/` with links to the blueprint, docs, and repository. Accept this only if the project will be published to GitHub Pages; otherwise decline.
- offer to write `.github/workflows/blueprint.yml` and create a git commit. Accept the workflow if publishing to GitHub Pages; otherwise decline and explain why.

After this step the layout under `blueprint/src/` is:

```
blueprint/src/
  web.tex            preamble for the HTML build (plasTeX)
  print.tex          preamble for the PDF build (xelatex/lualatex)
  content.tex        ← you write here
  macros/common.tex  macros shared by both
  macros/web.tex     macros only for HTML
  macros/print.tex   macros only for PDF
  plastex.cfg        plasTeX config (don't edit unless you know why)
```

## 4. Write the Lean statements

For every definition, lemma, and the target theorem, add a Lean declaration to the appropriate file in the project's Lean library. **Statements only — every proof body is `sorry`.** The mathematician's job is to either fill the `sorry`s themselves or to point out that a statement is wrong.

Rules:

- Use Mathlib idioms where they exist. Do not redefine a notion that Mathlib already has.
- Each declaration must be a real, type-checkable Lean 4 declaration — the final `checkdecls` step will fail otherwise. Run `lake build` after writing and fix every error before moving on. A `sorry` is fine; an unbound identifier is not.
- Name declarations so the names will be stable: `Project.lemma_name`, snake_case, namespaced. The blueprint will reference these names verbatim via `\lean{...}`; renames later mean editing two places.
- If a statement uses a non-trivial type you also had to introduce, write the `def` (or `structure`/`class`) in the same file or a sibling file, and include it in the blueprint as a definition node.

After writing, run `lake build` and confirm it succeeds (with `sorry` warnings, which are expected).

## 5. Write the LaTeX blueprint content

Edit `blueprint/src/content.tex`. For each Lean declaration you wrote, add a matching LaTeX environment. The mapping is one-to-one: every declaration the mathematician needs to audit appears in the blueprint.

The four macros that wire LaTeX to Lean and to the dependency graph are:

| Macro | Meaning |
|---|---|
| `\lean{Foo.bar}` | Names the Lean declaration(s) corresponding to this environment. Pass multiple comma-separated names if a statement maps to several. |
| `\leanok` | Asserts the surrounding environment is fully formalized in Lean. **Do not emit this** for environments whose Lean body is `sorry` — the mathematician adds it when they discharge the `sorry`. |
| `\uses{label1, label2}` | Lists LaTeX labels this environment depends on. Drives the dependency graph. Put inside a `theorem`/`lemma`/`definition` to mark statement-level deps; put inside a `proof` to mark deps used only in the proof. |
| `\notready` | Marks an environment as not yet ready for formalization (blueprint side is incomplete). |

Skeleton for a lemma:

```latex
\begin{lemma}
  \label{lem:descriptive_name}
  \lean{Project.descriptive_name}
  \uses{def:foo, lem:earlier_step}
  Statement in English, with full $\LaTeX$ math.
\end{lemma}

\begin{proof}
  \uses{lem:another_step}
  Proof sketch in English. Several sentences. Enough that the mathematician
  can tell whether the argument is right without reading the Lean.
\end{proof}
```

Important details about the graph semantics — get these wrong and the graph lies:

- A node's **border** color comes from statement-level state (`\leanok` outside any proof / `\notready` / all-deps-ready). A node's **fill** color comes from proof-level state. Definitions are special-cased: their fill uses the "defined" palette instead of "proved".
- `\uses` inside a `\begin{theorem}...\end{theorem}` declares **statement** dependencies. `\uses` inside `\begin{proof}...\end{proof}` declares **proof** dependencies. A node can have both. The distinction matters: it's what lets the graph show "this statement is ready to formalize even though its proof isn't".
- A proof that doesn't immediately follow its statement needs `\proves{lem:label}` so the package can pair them.
- If you want to point at an open issue for discussion, add `\discussion{42}` — it renders as a link to issue #42 in the project's GitHub repo.

Group related content into LaTeX `\section`s or `\chapter`s; the graph still works across them.

## 6. Build and verify

Run, in order:

```bash
lake build                      # the Lean side must compile (sorry warnings OK)
leanblueprint pdf               # PDF build via latexmk
leanblueprint web               # HTML build via plasTeX
leanblueprint checkdecls        # verifies every \lean{...} name exists in Lean
```

Or run all four at once with `leanblueprint all`.

`checkdecls` is the load-bearing verification step. It reads `blueprint/lean_decls` (auto-generated by the plugin during `web`) and confirms each name exists. **A green `checkdecls` is the minimum bar for handing the blueprint back to the mathematician.** If it fails, fix the LaTeX `\lean{...}` to match the actual Lean name, or fix the Lean name; do not delete the `\lean{...}` to silence the error.

Then serve and inspect:

```bash
leanblueprint serve             # http://localhost:8000
```

Open the dependency graph page. Sanity-check:

- Every node you wrote is present.
- Every edge corresponds to a real `\uses{...}`.
- No node is the wrong color — e.g. an orange ("not ready") node you didn't intend means a `\uses` references a label that doesn't exist.
- The target theorem sits at the top of its connected component and its ancestor closure looks like what the mathematician described.

## 7. Hand back to the mathematician

In your final message to the user, include:

1. A one-paragraph summary of what you formalized.
2. The list of Lean declarations you added, by name.
3. The path to the rendered blueprint (HTML in `blueprint/web/`, PDF in `blueprint/print/print.pdf`), or the GitHub Pages URL if CI is set up.
4. **An explicit list of gaps** — places where the mathematician's sketch was ambiguous and you guessed, places where you introduced a definition they didn't specify, and every `sorry` you left. Do not bury this. The mathematician's first action will be to audit these.
5. Suggestions for which lemma to formalize first (typically a leaf of the dependency graph).

## Anti-patterns to avoid

- **Don't emit `\leanok` for a statement you left as `sorry`.** The whole point of the graph is to track what's actually proved; lying breaks the tool.
- **Don't invent intermediate lemmas the mathematician didn't ask for** just to make the graph prettier. Ask first.
- **Don't paraphrase the target theorem.** The LaTeX statement and the Lean statement must be equivalent up to standard notation; if you had to weaken or strengthen anything, say so in the handback.
- **Don't skip `checkdecls`.** A blueprint that builds but whose `\lean{...}` names are wrong is silently broken.
- **Don't commit on the user's behalf** unless they asked. `leanblueprint new` will offer to commit; respect their answer. Subsequent edits stay uncommitted until they say otherwise.
- **Don't edit `plastex.cfg`, the `macros/` files, or `print.tex`/`web.tex` preambles** unless the mathematician asks for a specific change (e.g. extra packages). The defaults are deliberate.
