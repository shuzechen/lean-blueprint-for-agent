"""Smoke test for Plan A.

Builds a minimal BlueprintInput against Noisy_Channel_Coding/ (2 definitions +
1 theorem), runs the same code path the MCP `call_tool` handler runs
(scaffold + sidecar + plastex), then asserts:

  - blueprint/lean_sources.json was written with the expected keys
  - the rendered HTML contains the embedded Lean source (an import line
    that came from Def_DMC.lean)
  - the rendered HTML contains NO doc-gen-style URLs anywhere

Run from the repo root:

    LEANBLUEPRINT_PROJECT=$PWD/Noisy_Channel_Coding python scripts/smoke_test_plan_a.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from leanblueprint_mcp.schema import BlueprintInput
from leanblueprint_mcp.generator import scaffold, write_lean_sources_sidecar
from leanblueprint_mcp.build import build_web, check_dependencies


REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECT_DIR = (REPO_ROOT / "Noisy_Channel_Coding").resolve()


INPUT = {
    "title": "Noisy-Channel Coding Theorem (smoke test)",
    "author": "Smoke Test",
    "github": "https://github.com/shuzechen/lean-blueprint-for-agent",
    "chapters": [
        {
            "name": "Information-Theoretic Preliminaries",
            "items": [
                {
                    "id": "dmc",
                    "type": "definition",
                    "name": "Discrete Memoryless Channel",
                    "statement": (
                        "A DMC consists of finite alphabets $X, Y$ and a stochastic "
                        "kernel $W : X \\to Y \\to \\mathbb{R}$ with $\\sum_y W(y|x) = 1$."
                    ),
                    "status": "stated",
                    "lean": {"file": "Definitions/Def_DMC.lean"},
                },
                {
                    "id": "entropy",
                    "type": "definition",
                    "name": "Shannon entropy",
                    "statement": (
                        "For a finite PMF $p$, $H(p) = -\\sum_x p(x) \\log_2 p(x)$."
                    ),
                    "status": "stated",
                    "lean": {"file": "Definitions/Def_Entropy.lean"},
                },
            ],
        },
        {
            "name": "Converse",
            "items": [
                {
                    "id": "fano",
                    "type": "lemma",
                    "name": "Fano's inequality",
                    "statement": (
                        "$H(W \\mid Y) \\leq H(P_e) + P_e \\log(|\\mathcal{W}| - 1)$."
                    ),
                    "uses": ["dmc", "entropy"],
                    "status": "not_ready",
                    "lean": {"file": "Theorems/Thm_fano_inequality.lean"},
                },
            ],
        },
    ],
}


def main() -> int:
    if not PROJECT_DIR.exists():
        print(f"FAIL: {PROJECT_DIR} not found")
        return 1

    dep_errors = check_dependencies()
    if dep_errors:
        print("FAIL: dependency check:")
        for e in dep_errors:
            print(f"  - {e}")
        return 1

    inp = BlueprintInput.model_validate(INPUT)
    src_dir = PROJECT_DIR / "blueprint" / "src"

    scaffold(src_dir, inp)
    counts = write_lean_sources_sidecar(PROJECT_DIR, inp)
    print(f"sidecar: included={counts['included']} missing={counts['missing']}")

    sidecar_path = PROJECT_DIR / "blueprint" / "lean_sources.json"
    assert sidecar_path.exists(), "lean_sources.json was not written"
    sidecar = json.loads(sidecar_path.read_text())
    print(f"sidecar keys: {sorted(sidecar.keys())}")
    expected_keys = {"Def_DMC", "Def_Entropy", "Thm_fano_inequality"}
    missing = expected_keys - set(sidecar.keys())
    assert not missing, f"sidecar missing keys: {missing}"
    assert "Mathlib.Data.Real.Basic" in sidecar["Def_DMC"]["imports"], \
        f"Def_DMC imports: {sidecar['Def_DMC']['imports']}"
    print("OK: sidecar shape")

    result = build_web(PROJECT_DIR)
    print(f"build_web: success={result.success}")
    if not result.success:
        print("STDOUT:", result.stdout[-2000:])
        print("STDERR:", result.stderr[-2000:])
        return 1

    out_dir = Path(result.output_path)
    html_files = sorted(out_dir.glob("*.html"))
    assert html_files, f"no HTML files in {out_dir}"
    print(f"rendered: {len(html_files)} html file(s)")

    combined = "\n".join(p.read_text(encoding="utf-8") for p in html_files)

    assert "Mathlib.Data.Real.Basic" in combined, \
        "Lean import line did not appear in any rendered HTML"
    print("OK: import line embedded in HTML")

    assert "lean_source" in combined, "no .lean_source class block in HTML"
    print("OK: lean_source block present")

    forbidden = ["mathlib4_docs", "doc-gen", "/find/#doc/"]
    for f in forbidden:
        assert f not in combined, (
            f"FAIL: doc-gen URL fragment {f!r} found in rendered HTML"
        )
    print("OK: no doc-gen URLs in HTML")

    return 0


if __name__ == "__main__":
    sys.exit(main())
