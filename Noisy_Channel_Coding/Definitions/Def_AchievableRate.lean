import Definitions.Def_Code
import Mathlib.Algebra.Order.Floor.Defs
import Mathlib.Algebra.Order.Archimedean.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-!
# Achievable rates

A rate `R : ℝ` (in bits per channel use, `R ≥ 0`) is **achievable** for a DMC
`C` if for every `ε > 0` there exists a block length `n` and an
$(\lceil 2^{nR} \rceil, n)$-code whose maximum probability of error is at
most `ε`.

We use `⌈2^{nR}⌉` (`Nat.ceil`) for the codebook size, so that the rate
$\frac{\log_2 M_n}{n} \to R$ as $n \to \infty$ for any real `R ≥ 0`.

Because `Code.maxError` is *total* (returns `0` when `M = 0`), the
quantifier over codes does not need an explicit nonemptiness side-condition.
-/

open scoped BigOperators

/-- A real-valued rate `R ≥ 0` is **achievable** for the DMC `C` iff for every
    `ε > 0` there is some block length `n` and a code of size
    `⌈2^{nR}⌉` whose maximum error is `≤ ε`. -/
def Achievable {X Y : Type*} [Fintype X] [Fintype Y]
    (C : DMC X Y) (R : ℝ) : Prop :=
  0 ≤ R ∧
  ∀ ε : ℝ, 0 < ε →
    ∃ n : ℕ, 0 < n ∧
      let M : ℕ := ⌈(2 : ℝ) ^ ((n : ℝ) * R)⌉₊
      ∃ code : Code X Y C M n, code.maxError ≤ ε
