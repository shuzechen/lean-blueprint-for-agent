# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this package is

`leanblueprint` is a [plasTeX](https://github.com/plastex/plastex/) plugin plus a CLI for authoring blueprints of Lean 4 formalization projects. A blueprint is a LaTeX document that mirrors the structure of a Lean project, annotates each statement/proof with formalization status, and renders a hyperlinked HTML site (with a dependency graph) and a PDF.

The package has two faces that should not be conflated:

1. **The plasTeX plugin** (`leanblueprint/Packages/blueprint.py`) — loaded by plasTeX when a TeX document does `\usepackage{blueprint}`. Defines TeX commands (`\lean`, `\leanok`, `\uses`, `\notready`, `\discussion`, `\home`, `\github`, `\dochome`, `\graphcolor`, `\mathlibok`) and post-parse callbacks that compute node colors, formalization-readiness flags, and the `lean_decls` file consumed by `checkdecls`.
2. **The `leanblueprint` CLI** (`leanblueprint/client.py`, entry point `safe_cli`) — a `rich_click` Group used *inside an end-user Lean project* (not this repo). Subcommands: `new` (scaffolds `blueprint/` from Jinja2 templates and optionally edits `lakefile.lean` + writes a GitHub Actions workflow), `pdf`, `web`, `checkdecls`, `all`, `serve`.

The CLI assumes it is run from inside a Lean project with either a `lakefile.lean` or a `lakefile.toml`; it refuses to run otherwise. **Module import has this side effect** — `client.py` resolves `repo = Repo(".", search_parent_directories=True)` at import time, picks a `Lakefile` subclass (`LakefileLean` or `LakefileToml`, with `lakefile.lean` winning if both exist), and `sys.exit`s if neither file is found. This means `import leanblueprint.client` from inside *this* repo (which has no lakefile) will exit. Tests and tooling have to account for this.

## Common commands

There are no tests, no lint script, and no CI for this package itself (the `.github/workflows/blueprint.yml` in this repo is a *template* shipped to end users, not CI for the package). The repo is installed as a library/CLI by the user.

- Install for end users: `pip install leanblueprint` (published on PyPI; `setup.cfg` is at 0.0.20).
- Install in editable mode for development: `pip install -e .`
- Build backend is `setuptools` configured via `pyproject.toml` + `setup.cfg`; `setup.py` is a vestigial stub.
- Build the SCSS for the dep-graph styling (rarely needed; output is committed to `leanblueprint/static/`): use any `sass` CLI on `sass/dep_graph.scss`.
- Lint: `pylint` is configured via `.pylintrc` but is not wired to CI. Run `pylint leanblueprint` manually if needed.

To exercise the CLI end-to-end you need an external Lean project (a directory containing `lakefile.lean` and a git repo). From inside that project:

- `leanblueprint new` — scaffold `blueprint/src/` from `leanblueprint/templates/`
- `leanblueprint pdf` — runs `latexmk` inside `blueprint/src` outputting to `blueprint/print`
- `leanblueprint web` — runs `plastex -c plastex.cfg web.tex` inside `blueprint/src`
- `leanblueprint checkdecls` — runs `lake exe checkdecls blueprint/lean_decls` (requires a prior `lake build`)
- `leanblueprint all` — pdf + web + `lake build` + checkdecls
- `leanblueprint serve` — serves the compiled `blueprint/web` on the first free port in 8000–8009
- Pass `--debug` to surface Python tracebacks instead of the friendly error path in `safe_cli`/`handle_exception`.

## Architecture notes worth knowing before editing

### Dependency graph state lives on plasTeX node `userdata`

Most of the package's value is in the post-parse callback `make_lean_data` (`leanblueprint/Packages/blueprint.py:196`). For every node in the depgraph it derives:

- `lean_urls`: `(decl, url)` pairs pointing into the project's doc-gen output (`project_dochome`, defaulting to mathlib4_docs).
- `can_state`: all referenced nodes are `leanok` and this node is not `notready`.
- `can_prove` / `proved`: derived from `proved_by` (set by the depgraph plugin) and the proof's own `uses` / `leanok`.
- `fully_proved`: ancestor closure check — this node and every ancestor are either proved or definitions.

The `colorizer` (node border) and `fillcolorizer` (node fill) closures in `ProcessOptions` consume these flags. **Definitions are special-cased** in `fillcolorizer`: they use the `defined` / `can_state` palette instead of `proved` / `can_prove`. The default palette is overridable from TeX via `\graphcolor{node_type}{color}{description}`.

`make_lean_data` also writes `blueprint/lean_decls` — a newline-separated list of every name passed to `\lean{...}`, which `checkdecls` then verifies against the compiled Lean project.

### Plugin loading is implicit

`ProcessOptions` (`leanblueprint/Packages/blueprint.py:170`) mutates `document.config['general'].data['plugins']` to append `plastexdepgraph` (and `plastexshowmore` if the `showmore` option is set) before loading them. This is intentional backward-compat for projects that wrote `\usepackage{blueprint}` before the depgraph package was split out — preserve this behavior.

### `client.py new` writes outside `blueprint/`

`leanblueprint new` is not a pure scaffold. In addition to filling `blueprint/src/` from `leanblueprint/templates/`, it conditionally:

- mutates the user's lakefile via the `Lakefile.add_checkdecls()` / `Lakefile.add_docgen()` methods. The Lean and TOML lakefile flavors have separate implementations (`LakefileLean` does text append; `LakefileToml` edits the parsed TOML via `tomlkit`). When changing the lakefile-edit behavior, update **both** subclasses.
- runs `lake update checkdecls` and `lake -R -Kenv=dev update doc-gen4` as separate prompts.
- optionally writes a Jekyll home page to `home_page/` from `leanblueprint/jekyll_templates/`. This uses **different** Jinja2 delimiters than the main templates — `{|...|}` for variables and `{%|...|%}` for blocks — because Jekyll/Liquid uses `{{ }}` and `{% %}` itself. Don't confuse the two delimiter sets.
- writes `.github/workflows/blueprint.yml` from `leanblueprint/templates/blueprint.yml`.
- creates a git commit including the lakefile, manifest, blueprint dir, `home_page/` (if created), and workflow file.

Any change to these side effects affects existing users' repos on the next `leanblueprint new`.

### Jinja2 template delimiters are non-standard, and differ between template sets

Templates under `leanblueprint/templates/` use `{| ... |}` for variables and `{-- ... --}` for comments (configured in `client.py` `new()`). This avoids collisions with LaTeX's `{{ }}` and `%` syntax.

Templates under `leanblueprint/jekyll_templates/` additionally override the block delimiters to `{%| ... |%}` so Jekyll's Liquid `{% %}` syntax can pass through untouched at render time. **The two template directories use different Environments — don't copy a template from one to the other without re-checking which delimiters its surrounding files expect.**

### `templates/blueprint.yml` is excluded from the generic loop

In `client.py new()`, the loop that copies templates explicitly skips `blueprint.yml` (`if tpl_name.endswith("blueprint.yml"): continue`) because it must land in `.github/workflows/`, not `blueprint/src/`. If you add new top-level templates with a similar destination, follow the same pattern.

### Packaging

Non-Python assets are shipped via `MANIFEST.in` — templates, static CSS, renderer templates, and the Jekyll template tree. New asset directories must be added there or they will be missing from a `pip install`. `setup.cfg` is the source of truth for metadata, dependencies (note `tomlkit` is required for `lakefile.toml` support), and the console-script entry point; `pyproject.toml` declares the build backend; `setup.py` is a vestigial stub.
