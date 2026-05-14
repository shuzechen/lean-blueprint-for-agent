import Definitions.Def_DMC
import Mathlib.Analysis.SpecialFunctions.Log.Base

/-!
# Shannon entropy and conditional entropy (discrete, finite case)

For a probability mass function `p : α → ℝ` on a finite type `α`, the
**Shannon entropy** in bits is
$$H(p) = -\sum_a p(a)\, \log_2 p(a)$$
with the convention $0 \log_2 0 = 0$ — handled automatically because
`Real.log 0 = 0` in Mathlib.

For a joint distribution `q : α → β → ℝ` on `α × β`, the **conditional
entropy** of the second coordinate given the first is
$$H(Y\mid X) = -\sum_{a,b} q(a,b) \log_2 \frac{q(a,b)}{\sum_{b'} q(a,b')}.$$
-/

open scoped BigOperators
open Real

/-- Shannon entropy (in bits) of a finitely-supported probability mass
    function `p : α → ℝ`. The argument is bare `α → ℝ`; correctness only
    requires `p ≥ 0` and `∑ p = 1`, which the lemmas asserting properties
    of `entropy` will demand. -/
noncomputable def entropy {α : Type*} [Fintype α] (p : α → ℝ) : ℝ :=
  - ∑ a, p a * Real.logb 2 (p a)

/-- The joint distribution on `X × Y` induced by an input pmf `pX` on `X` and
    a channel `W : X → Y → ℝ`. -/
def jointDist {X Y : Type*} [Fintype X] [Fintype Y]
    (pX : X → ℝ) (W : X → Y → ℝ) : X → Y → ℝ :=
  fun x y => pX x * W x y

/-- The output marginal `pY(y) = ∑ₓ pX(x) W(y|x)` induced by an input pmf
    and a channel. -/
def outputMarginal {X Y : Type*} [Fintype X] [Fintype Y]
    (pX : X → ℝ) (W : X → Y → ℝ) : Y → ℝ :=
  fun y => ∑ x, pX x * W x y

/-- Conditional Shannon entropy `H(Y | X)` (in bits), for an input pmf `pX`
    and a channel `W : X → Y → ℝ`. This is the average uncertainty in `Y`
    given knowledge of `X`. -/
noncomputable def condEntropy {X Y : Type*} [Fintype X] [Fintype Y]
    (pX : X → ℝ) (W : X → Y → ℝ) : ℝ :=
  - ∑ x, ∑ y, pX x * W x y * Real.logb 2 (W x y)
