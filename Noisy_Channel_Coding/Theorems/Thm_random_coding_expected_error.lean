import Definitions.Def_ChannelCapacity
import Definitions.Def_Code

/-!
# Random coding: expected average error tends to 0 below capacity

Cover & Thomas §7.7. With codewords drawn i.i.d. from `pX⊗ⁿ` and
jointly-typical decoding at tolerance `ε`, the expected average probability
of error (over random codebooks) satisfies, for all `n` large enough,
$$\mathbb{E}_{\mathcal{C}}[\bar P_e^{(n)}] \;\le\; 4\varepsilon$$
provided the rate `R < I(p_X, W)`. In particular there exists a deterministic
codebook of size $\lceil 2^{nR}\rceil$ achieving average error at most
`4ε`.

This is the workhorse of the achievability proof: the existence of *some*
$(\lceil 2^{nR}\rceil, n)$ code with small **average** error. The bridge to
small **max** error is `Thm_expurgation_max_from_average`.
-/

open scoped BigOperators

/-- **Random coding theorem (existence form).**
    For every input pmf `pX`, every `ε > 0`, and every rate `R` strictly less
    than the mutual information `I(pX; W)`, there is a sufficiently large
    block length `n` and a deterministic $(\lceil 2^{nR}\rceil, n)$ code
    whose **average** probability of error is at most `ε`. -/
theorem random_coding_expected_error
    {X Y : Type*} [Fintype X] [Fintype Y]
    (C : DMC X Y) (pX : FinPMF X) (R : ℝ) (hR : 0 ≤ R)
    (hRI : R < mutualInformation pX.toFun C.W) :
    ∀ ε : ℝ, 0 < ε →
      ∃ n : ℕ, 0 < n ∧
        ∃ (hM : 0 < (⌈(2 : ℝ) ^ ((n : ℝ) * R)⌉₊))
          (code : Code X Y C ⌈(2 : ℝ) ^ ((n : ℝ) * R)⌉₊ n),
          haveI : NeZero (⌈(2 : ℝ) ^ ((n : ℝ) * R)⌉₊) := ⟨Nat.pos_iff_ne_zero.mp hM⟩
          code.avgError ≤ ε := by
  sorry
