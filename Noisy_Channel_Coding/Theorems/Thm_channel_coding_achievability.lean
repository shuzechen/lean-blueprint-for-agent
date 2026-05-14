import Definitions.Def_ChannelCapacity
import Definitions.Def_AchievableRate

/-!
# Achievability direction of Shannon's theorem

Every nonnegative rate strictly below the channel capacity is achievable.
(The boundary case `R = C` is deferred — see the project CLAUDE.md.)
-/

/-- **Achievability.** Every nonnegative rate strictly below the channel
    capacity is achievable. -/
theorem channel_coding_achievability
    {X Y : Type*} [Fintype X] [Fintype Y] [Nonempty X]
    (C : DMC X Y) :
    ∀ R : ℝ, 0 ≤ R → R < channelCapacity C → Achievable C R := by
  sorry
