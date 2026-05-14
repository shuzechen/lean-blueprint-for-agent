import Definitions.Def_Code

/-!
# Expurgation: passing from average to maximum error

Cover & Thomas §7.7.2 / Shannon's expurgation step. If a code of size `2M`
has average error `≤ ε`, then by dropping the worst-half of its codewords
we obtain a code of size `M` whose **maximum** error is `≤ 2ε`.
-/

open scoped BigOperators

/-- **Expurgation lemma.** Given an `(2M, n)` code whose *average* error is
    `≤ ε`, there exists an `(M, n)` sub-code (obtained by keeping the better
    half of the messages) whose *maximum* error is `≤ 2 ε`. -/
theorem expurgation_max_from_average
    {X Y : Type*} [Fintype X] [Fintype Y]
    (C : DMC X Y) {M n : ℕ} (hM : 0 < M)
    (code2M : Code X Y C (2 * M) n) (ε : ℝ)
    (havg : code2M.avgError ≤ ε) :
    ∃ subcode : Code X Y C M n, subcode.maxError ≤ 2 * ε := by
  sorry
