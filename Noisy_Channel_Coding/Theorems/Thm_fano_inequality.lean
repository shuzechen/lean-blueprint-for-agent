import Definitions.Def_Entropy

/-!
# Fano's inequality

For random variables `W, Ŵ` on a finite alphabet of size `M`, with
error probability $P_e = \Pr(\hat W \ne W)$,
$$H(W \mid \hat W) \;\le\; H_2(P_e) \,+\, P_e \log_2 (M - 1)
                       \;\le\; 1 \,+\, P_e \log_2 M.$$

We use the slightly weaker but more convenient second form
`H(W|Ŵ) ≤ 1 + P_e · log₂ M`. The proof is the same chain-rule manipulation
of conditional entropies.
-/

open scoped BigOperators

/-- **Fano's inequality.** For a joint pmf `q` on `Fin M × Fin M` representing
    the (possibly random) message `W` and its estimate `Ŵ`, the conditional
    entropy of `W` given `Ŵ` is bounded by `1 + P_e · log₂ M`, where
    `P_e = Pr(W ≠ Ŵ)`. -/
theorem fano_inequality
    {M : ℕ} (hM : 0 < M)
    (q : Fin M → Fin M → ℝ)
    (hq_nonneg : ∀ i j, 0 ≤ q i j)
    (hq_sum_one : ∑ i, ∑ j, q i j = 1) :
    let Pe := ∑ i, ∑ j, (if i ≠ j then q i j else 0)
    condEntropy (fun i => ∑ j, q i j) (fun i j => q i j / (∑ j', q i j'))
      ≤ 1 + Pe * Real.logb 2 (M : ℝ) := by
  sorry
