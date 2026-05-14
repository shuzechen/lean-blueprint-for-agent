import Definitions.Def_MutualInformation

/-!
# Joint AEP — Property 1: the jointly-typical set has high probability

Let `pX` be an input pmf, `W` a channel, and `q := jointDist pX W` the joint
distribution on `X × Y`. Draw `(X^n, Y^n)` i.i.d. from `q`. The jointly
$\varepsilon$-typical set
$$A_\varepsilon^{(n)} = \Big\{(x^n,y^n) : \big|-\tfrac{1}{n}\log q^n(x^n,y^n) -
H(X,Y)\big| < \varepsilon,\ \ldots\Big\}$$
has probability tending to 1.

This is one of three "joint AEP" properties used in the random-coding argument.
We state it abstractly as: for every `ε > 0` and every `δ > 0`, there is
`n₀` such that for all `n ≥ n₀`, the probability under `q⊗ⁿ` of the jointly-
typical set is `> 1 − δ`.
-/

open scoped BigOperators

/-- Joint $\varepsilon$-typical set for the joint distribution `q` on `X × Y`.

  `(x^n, y^n) ∈ A_ε^{(n)}` iff all three quantities

  * `-(1/n) log p(x^n)`     is within `ε` of `H(X)`,
  * `-(1/n) log p(y^n)`     is within `ε` of `H(Y)`,
  * `-(1/n) log q(x^n,y^n)` is within `ε` of `H(X,Y)`,

  where `p(x^n) = ∏ pX(xᵢ)`, `p(y^n) = ∏ pY(yᵢ)`, `q(x^n,y^n) = ∏ q(xᵢ,yᵢ)`. -/
noncomputable def jointlyTypicalSet
    {X Y : Type*} [Fintype X] [Fintype Y]
    (pX : X → ℝ) (W : X → Y → ℝ) (ε : ℝ) (n : ℕ) :
    Finset ((Fin n → X) × (Fin n → Y)) := by
  classical
  exact (Finset.univ : Finset ((Fin n → X) × (Fin n → Y))).filter (fun xy =>
    let xn := xy.1
    let yn := xy.2
    let q := jointDist pX W
    let pY := outputMarginal pX W
    let logp_x := -(1 / (n : ℝ)) * Real.log (∏ i, pX (xn i))
    let logp_y := -(1 / (n : ℝ)) * Real.log (∏ i, pY (yn i))
    let logp_q := -(1 / (n : ℝ)) * Real.log (∏ i, q (xn i) (yn i))
    |logp_x - entropy pX| < ε ∧
    |logp_y - entropy pY| < ε ∧
    |logp_q - entropy (fun (xy : X × Y) => q xy.1 xy.2)| < ε)

/-- **Joint AEP — high-probability property.** For every `ε > 0` and `δ > 0`,
    for all sufficiently large `n`, the probability under the i.i.d. joint
    distribution `q⊗ⁿ` of landing in the jointly-typical set exceeds `1 − δ`. -/
theorem joint_aep_high_probability
    {X Y : Type*} [Fintype X] [Fintype Y]
    (pX : FinPMF X) (W : X → Y → ℝ)
    (hW_nonneg : ∀ x y, 0 ≤ W x y)
    (hW_sum : ∀ x, ∑ y, W x y = 1)
    (ε δ : ℝ) (hε : 0 < ε) (hδ : 0 < δ) :
    ∃ n₀ : ℕ, ∀ n : ℕ, n₀ ≤ n →
      (1 : ℝ) - δ <
        ∑ xy ∈ jointlyTypicalSet pX.toFun W ε n,
          (∏ i, jointDist pX.toFun W (xy.1 i) (xy.2 i)) := by
  sorry
