import Definitions.Def_ChannelCapacity
import Definitions.Def_AchievableRate

/-!
# Weak converse of Shannon's theorem

Every achievable rate is at most the channel capacity. Contrapositively,
no rate above capacity admits codes with vanishing maximum error.
-/

/-- **Weak converse.** Every achievable rate satisfies `R ≤ channelCapacity C`. -/
theorem channel_coding_converse
    {X Y : Type*} [Fintype X] [Fintype Y] [Nonempty X]
    (C : DMC X Y) :
    ∀ R : ℝ, Achievable C R → R ≤ channelCapacity C := by
  sorry
