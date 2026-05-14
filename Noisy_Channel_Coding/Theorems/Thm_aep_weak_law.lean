import Definitions.Def_Entropy

/-!
# Asymptotic Equipartition Property (AEP) — weak law form

For i.i.d. samples $X_1, X_2, \ldots$ drawn from a discrete distribution
`p` on a finite alphabet,
$$-\tfrac{1}{n} \log p(X_1,\ldots,X_n) \;\xrightarrow{\,p\,}\; H(p).$$

This is the foundational limit theorem behind the three joint-AEP lemmas
above. We state it abstractly as: the i.i.d. probability of the "atypical"
event vanishes as `n → ∞`.
-/

open scoped BigOperators

/-- **AEP (weak law).** For any `ε, δ > 0`, for all sufficiently large `n`,
    the probability under `p⊗ⁿ` of the set of sequences whose empirical log-
    likelihood deviates from `H(p)` by more than `ε` is at most `δ`. -/
theorem aep_weak_law
    {α : Type*} [Fintype α]
    (p : FinPMF α) (ε δ : ℝ) (hε : 0 < ε) (hδ : 0 < δ) :
    ∃ n₀ : ℕ, ∀ n : ℕ, n₀ ≤ n →
      (∑ xn ∈ (Finset.univ : Finset (Fin n → α)).filter (fun xn =>
              ε ≤ |(-(1 / (n : ℝ)) * Real.log (∏ i, p.toFun (xn i)))
                      - entropy p.toFun|),
          ∏ i, p.toFun (xn i)) ≤ δ := by
  sorry
