import Mathlib.Data.Fintype.BigOperators
import Mathlib.Data.Real.Basic

/-!
# Discrete Memoryless Channels

A **discrete memoryless channel** (DMC) is given by a finite input alphabet `X`,
a finite output alphabet `Y`, and a stochastic transition kernel
`W : X → Y → ℝ` satisfying `W x y ≥ 0` and `∑ y, W x y = 1` for every `x`.

The **n-fold product extension** `W ⊗ⁿ` acts independently on each coordinate:
`Wⁿ y⁽ⁿ⁾ ∣ x⁽ⁿ⁾  =  ∏ᵢ W (yᵢ ∣ xᵢ)`.

We model "input distribution" as a `pmf` on `X`, i.e. a nonneg function summing
to `1`. We do **not** use `PMF` from Mathlib here in order to keep the
underlying carrier `X → ℝ` and avoid `ℝ≥0∞` everywhere.
-/

open scoped BigOperators

/-- A probability mass function on a finite type, valued in `ℝ`. -/
structure FinPMF (α : Type*) [Fintype α] where
  toFun     : α → ℝ
  nonneg    : ∀ a, 0 ≤ toFun a
  sum_one   : ∑ a, toFun a = 1

namespace FinPMF
variable {α : Type*} [Fintype α]

instance : CoeFun (FinPMF α) (fun _ => α → ℝ) := ⟨FinPMF.toFun⟩

end FinPMF

/-- A **discrete memoryless channel** with input alphabet `X` and output
    alphabet `Y` (both finite): a stochastic transition matrix
    `W : X → Y → ℝ`. -/
structure DMC (X Y : Type*) [Fintype X] [Fintype Y] where
  W         : X → Y → ℝ
  nonneg    : ∀ x y, 0 ≤ W x y
  row_sum   : ∀ x, ∑ y, W x y = 1

namespace DMC
variable {X Y : Type*} [Fintype X] [Fintype Y]

/-- The `n`-fold product extension of a DMC: independent uses of the channel.
    `productKernel n W (x⁽ⁿ⁾) (y⁽ⁿ⁾) = ∏ᵢ W (xᵢ) (yᵢ)`. -/
def productKernel (n : ℕ) (C : DMC X Y) :
    (Fin n → X) → (Fin n → Y) → ℝ :=
  fun x y => ∏ i, C.W (x i) (y i)

end DMC
