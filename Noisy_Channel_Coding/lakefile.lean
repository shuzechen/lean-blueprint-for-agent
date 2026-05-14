import Lake
open Lake DSL

package «noisy-channel-coding» where
  leanOptions := #[
    ⟨`pp.unicode.fun, true⟩
  ]

require mathlib from "../mathlib4"

lean_lib Definitions where
  globs := #[.submodules `Definitions]

lean_lib Theorems where
  globs := #[.submodules `Theorems]

lean_lib Sketches where
  globs := #[.submodules `Sketches]
