"""JSON → LaTeX blueprint files generator."""

from __future__ import annotations

import os
from pathlib import Path

from .schema import BlueprintInput, BlueprintItem, ItemType


_TYPE_PREFIX: dict[ItemType, str] = {
    ItemType.theorem: "thm",
    ItemType.lemma: "lem",
    ItemType.proposition: "prop",
    ItemType.corollary: "cor",
    ItemType.definition: "def",
}

_TYPE_ENV: dict[ItemType, str] = {
    ItemType.theorem: "theorem",
    ItemType.lemma: "lemma",
    ItemType.proposition: "proposition",
    ItemType.corollary: "corollary",
    ItemType.definition: "definition",
}


def make_label(typ: ItemType, id_: str) -> str:
    return f"{_TYPE_PREFIX[typ]}:{id_}"


def _escape_latex(s: str) -> str:
    for ch, repl in [
        ("\\", "\\textbackslash "),
        ("&", "\\&"),
        ("%", "\\%"),
        ("$", "\\$"),
        ("#", "\\#"),
        ("_", "\\_"),
        ("{", "\\{"),
        ("}", "\\}"),
        ("~", "\\textasciitilde "),
        ("^", "\\textasciicircum "),
    ]:
        s = s.replace(ch, repl)
    return s


def generate_content(inp: BlueprintInput) -> str:
    id_to_type: dict[str, ItemType] = {}
    for ch in inp.chapters:
        for item in ch.items:
            id_to_type[item.id] = item.type

    def resolve_label(dep_id: str) -> str:
        t = id_to_type.get(dep_id)
        return make_label(t, dep_id) if t else f"???:{dep_id}"

    parts: list[str] = []

    for ch in inp.chapters:
        parts.append(f"\\chapter{{{_escape_latex(ch.name)}}}")
        parts.append("")

        for item in ch.items:
            env = _TYPE_ENV[item.type]
            label = make_label(item.type, item.id)
            opt_title = f"[{_escape_latex(item.name)}]" if item.name else ""

            lines = [f"\\begin{{{env}}}{opt_title}", f"  \\label{{{label}}}"]

            if item.uses:
                labels = ", ".join(resolve_label(d) for d in item.uses)
                lines.append(f"  \\uses{{{labels}}}")

            if item.lean_decls:
                lines.append(f"  \\lean{{{', '.join(item.lean_decls)}}}")

            status_cmds = {
                "stated": "  \\leanok",
                "not_ready": "  \\notready",
                "mathlib": "  \\mathlibok",
            }
            lines.append(status_cmds[item.status.value])

            if item.discussion is not None:
                lines.append(f"  \\discussion{{{item.discussion}}}")

            lines.append(f"  {item.statement}")
            lines.append(f"\\end{{{env}}}")

            if item.proof:
                lines.append("\\begin{proof}")
                lines.append(f"  \\proves{{{label}}}")
                lines.append(f"  {item.proof}")
                lines.append("\\end{proof}")

            parts.append("\n".join(lines))
            parts.append("")

    return "\n".join(parts)


def generate_web_tex(inp: BlueprintInput) -> str:
    home = inp.home or "https://example.com"
    github = inp.github or "https://github.com/user/repo"
    dochome = inp.dochome or "https://leanprover-community.github.io/mathlib4_docs"
    author_line = f"\\author{{{_escape_latex(inp.author)}}}" if inp.author else ""

    return f"""% Web version of the blueprint
\\documentclass{{report}}

\\usepackage{{amssymb, amsthm, amsmath}}
\\usepackage{{hyperref}}
\\usepackage[dep_graph]{{blueprint}}

\\input{{macros/common}}
\\input{{macros/web}}

\\home{{{home}}}
\\github{{{github}}}
\\dochome{{{dochome}}}

\\title{{{_escape_latex(inp.title)}}}
{author_line}

\\begin{{document}}
\\maketitle
\\input{{content}}
\\end{{document}}
"""


def generate_print_tex(inp: BlueprintInput) -> str:
    author_line = f"\\author{{{_escape_latex(inp.author)}}}" if inp.author else ""

    return f"""% Printable version of the blueprint
\\documentclass[a4paper]{{report}}

\\usepackage{{geometry}}
\\usepackage{{expl3}}
\\usepackage{{amssymb, amsthm, mathtools}}
\\usepackage[unicode,colorlinks=true,linkcolor=blue,urlcolor=magenta,citecolor=blue]{{hyperref}}
\\usepackage[warnings-off={{mathtools-colon,mathtools-overbracket}}]{{unicode-math}}

\\input{{macros/common}}
\\input{{macros/print}}

\\title{{{_escape_latex(inp.title)}}}
{author_line}

\\begin{{document}}
\\maketitle
\\input{{content}}
\\end{{document}}
"""


COMMON_MACROS = r"""% Macros shared by web and print versions
\newtheorem{theorem}{Theorem}
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}

\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}
"""

WEB_MACROS = r"""% Web-only macros
"""

PRINT_MACROS = r"""% Print-only macros: dummy definitions for blueprint commands
\newcommand{\lean}[1]{}
\newcommand{\discussion}[1]{}
\newcommand{\leanok}{}
\newcommand{\mathlibok}{}
\newcommand{\notready}{}
\ExplSyntaxOn
\NewDocumentCommand{\uses}{m}
 {\clist_map_inline:nn{#1}{\vphantom{\ref{##1}}}%
  \ignorespaces}
\NewDocumentCommand{\proves}{m}
 {\clist_map_inline:nn{#1}{\vphantom{\ref{##1}}}%
  \ignorespaces}
\ExplSyntaxOff
"""

PLASTEX_CFG = """[general]
renderer=HTML5
copy-theme-extras=yes
plugins=plastexdepgraph leanblueprint

[document]
toc-depth=2
toc-non-files=True

[files]
directory=../web/
split-level=0

[html5]
localtoc-level=0
extra-css=extra_styles.css
mathjax-dollars=False
"""

LATEXMKRC = r"""# latexmk configuration for pdf blueprint
$pdf_mode = 1;
$pdflatex = 'xelatex -synctex=1';
@default_files = ('print.tex');
"""

BLUEPRINT_STY = r"""\DeclareOption*{}
\ProcessOptions

\newcommand{\graphcolor}[3]{}
"""

EXTRA_STYLES_CSS = """/* CSS tweaks for this blueprint */
div.theorem_thmcontent {
\tborder-left: .15rem solid black;
}

div.proposition_thmcontent {
\tborder-left: .15rem solid black;
}

div.lemma_thmcontent {
\tborder-left: .1rem solid black;
}

div.corollary_thmcontent {
\tborder-left: .1rem solid black;
}

div.proof_content {
\tborder-left: .08rem solid grey;
}
"""


def scaffold(src_dir: Path, inp: BlueprintInput) -> None:
    macros_dir = src_dir / "macros"
    macros_dir.mkdir(parents=True, exist_ok=True)

    files: list[tuple[Path, str]] = [
        (src_dir / "web.tex", generate_web_tex(inp)),
        (src_dir / "print.tex", generate_print_tex(inp)),
        (src_dir / "content.tex", generate_content(inp)),
        (macros_dir / "common.tex", COMMON_MACROS),
        (macros_dir / "web.tex", WEB_MACROS),
        (macros_dir / "print.tex", PRINT_MACROS),
        (src_dir / "plastex.cfg", PLASTEX_CFG),
        (src_dir / "latexmkrc", LATEXMKRC),
        (src_dir / "blueprint.sty", BLUEPRINT_STY),
        (src_dir / "extra_styles.css", EXTRA_STYLES_CSS),
    ]

    for path, content in files:
        path.write_text(content, encoding="utf-8")
