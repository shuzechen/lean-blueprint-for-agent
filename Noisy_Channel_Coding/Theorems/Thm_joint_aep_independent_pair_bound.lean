import Theorems.Thm_joint_aep_high_probability

/-!
# Joint AEP — Property 2: independent codewords are rarely jointly typical

If $\tilde X^n \sim p_X^{\otimes n}$ is **independent** of $\tilde Y^n \sim
p_Y^{\otimes n}$ (i.e. drawn from the product of marginals rather than the
joint), then
$$\Pr\big((\tilde X^n, \tilde Y^n) \in A_\varepsilon^{(n)}\big)
   \;\le\; 2^{-n\,(I(X;Y)\,-\,3\varepsilon)}.$$

This is the bound that drives the achievability error analysis: a random
"wrong" codeword has only an exponentially small chance of being jointly
typical with the received output sequence.
-/

open scoped BigOperators

/-- **Joint AEP — independent-pair bound.**
    For independent sequences with the correct marginals, the probability of
    landing in the jointly-typical set is at most $2^{-n(I-3\varepsilon)}$. -/
theorem joint_aep_independent_pair_bound
    {X Y : Type*} [Fintype X] [Fintype Y]
    (pX : FinPMF X) (W : X → Y → ℝ)
    (hW_nonneg : ∀ x y, 0 ≤ W x y)
    (hW_sum : ∀ x, ∑ y, W x y = 1)
    (ε : ℝ) (hε : 0 < ε) (n : ℕ) :
    (∑ xy ∈ jointlyTypicalSet pX.toFun W ε n,
        (∏ i, pX.toFun (xy.1 i)) * (∏ i, outputMarginal pX.toFun W (xy.2 i)))
      ≤ (2 : ℝ) ^ (-(n : ℝ) * (mutualInformation pX.toFun W - 3 * ε)) := by
  sorry
