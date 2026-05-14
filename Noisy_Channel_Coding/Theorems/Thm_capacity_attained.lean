import Definitions.Def_ChannelCapacity

/-!
# The channel capacity supremum is attained

The function `pX ↦ I(p_X; W)` is continuous on the (compact) simplex of input
distributions, hence the supremum in `channelCapacity` is achieved.

This is a structural lemma used to convert `R < C` into `R < I(p_X^*; W)`
for some witness `p_X^*` — needed when invoking
`random_coding_expected_error`.
-/

/-- **Capacity is attained.** There exists an input pmf realizing the
    supremum that defines `channelCapacity C`. -/
theorem channel_capacity_attained
    {X Y : Type*} [Fintype X] [Fintype Y] [Nonempty X]
    (C : DMC X Y) :
    ∃ pX : FinPMF X, mutualInformation pX.toFun C.W = channelCapacity C := by
  sorry
