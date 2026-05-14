import Definitions.Def_DMC

/-!
# Block codes for a DMC

An `(M, n)`-**block code** for a DMC `C : DMC X Y` consists of an encoder
`enc : Fin M → (Fin n → X)` and a decoder `dec : (Fin n → Y) → Fin M`.

We define three probabilities of error:

* `errorPr C code i` — conditional error probability given message `i` was sent:
  $$\lambda_i \;=\; \sum_{y^n : \mathrm{dec}(y^n) \ne i} W^n(y^n \mid \mathrm{enc}(i)).$$
* `avgError` — uniform-average error $\bar P_e = \frac{1}{M}\sum_i \lambda_i$.
* `maxError` — maximum error $P_e^{(n)} = \max_i \lambda_i$ (defined to be `0` when
  `M = 0` so the function is total).

Both `errorPr` and the aggregate quantities live entirely inside this file.
-/

open scoped Classical
open scoped BigOperators

/-- A `(M, n)` block code for the DMC `C`: encoder + decoder. -/
structure Code (X Y : Type*) [Fintype X] [Fintype Y]
    (_C : DMC X Y) (M n : ℕ) where
  enc : Fin M → (Fin n → X)
  dec : (Fin n → Y) → Fin M

namespace Code

variable {X Y : Type*} [Fintype X] [Fintype Y]
variable {C : DMC X Y} {M n : ℕ}

/-- The conditional probability that the decoder errs given message `i` was
    transmitted, under the `n`-fold product channel. -/
noncomputable def errorPr (code : Code X Y C M n) (i : Fin M) : ℝ :=
  ∑ y : Fin n → Y,
    (if code.dec y ≠ i then (1 : ℝ) else 0) *
      DMC.productKernel n C (code.enc i) y

/-- Average probability of error, with the message chosen uniformly at random.
    Returns `0` when `M = 0` (vacuously no messages → no errors). -/
noncomputable def avgError (code : Code X Y C M n) : ℝ :=
  if M = 0 then 0
  else (1 / (M : ℝ)) * ∑ i, code.errorPr i

/-- Maximum probability of error over messages.
    Returns `0` when `M = 0` (vacuous max over empty index). -/
noncomputable def maxError (code : Code X Y C M n) : ℝ :=
  if hM : 0 < M then
    haveI : Nonempty (Fin M) := ⟨⟨0, hM⟩⟩
    Finset.univ.sup' Finset.univ_nonempty code.errorPr
  else 0

end Code
