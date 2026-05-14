import Definitions.Def_ChannelCapacity

/-!
# Mutual information across `n` uses of a DMC is bounded by `n · C`

The bridge from per-letter capacity to block mutual information. For any
input pmf `p_{X^n}` on `Xⁿ` (not necessarily product!) and the DMC's
product extension,
$$I(X^n;\, Y^n) \;\le\; n \cdot C(W).$$

This follows from the chain rule for mutual information and the memoryless
property: $I(X^n;Y^n) \le \sum_i I(X_i;Y_i) \le n \,C(W)$.
-/

open scoped BigOperators

/-- **Block mutual information is bounded by `n · C`.**
    For any input pmf on `Xⁿ` and the `n`-fold product extension of a DMC,
    the mutual information between the input block and output block is at
    most `n · channelCapacity C`. -/
theorem mutual_info_dmc_le_n_capacity
    {X Y : Type*} [Fintype X] [Fintype Y] [Nonempty X]
    (C : DMC X Y) (n : ℕ) (pXn : FinPMF (Fin n → X)) :
    mutualInformation pXn.toFun (DMC.productKernel n C)
      ≤ (n : ℝ) * channelCapacity C := by
  sorry
