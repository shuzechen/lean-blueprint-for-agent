import Definitions.Def_ChannelCapacity
import Definitions.Def_AchievableRate

/-!
# Shannon's Noisy-Channel Coding Theorem (top-level statement)

For any discrete memoryless channel `C : DMC X Y` (with nonempty input
alphabet) we have **both**:

* (Achievability) every rate strictly below capacity is achievable;
* (Weak converse) every achievable rate is at most capacity.

This is the textbook formulation from Cover & Thomas, Theorem 7.7.1. We
deliberately keep the two directions separate — the bi-conditional
`Achievable ↔ R ≤ C` would require an extra "achievability set is closed"
step at the boundary `R = C`, which we treat as future work.
-/

/-- **Shannon's Noisy-Channel Coding Theorem.** Statement combining
    Cover & Thomas's achievability (Thm 7.7.1) and weak converse (Thm 7.9.1)
    for a discrete memoryless channel. -/
theorem noisy_channel_coding_theorem
    {X Y : Type*} [Fintype X] [Fintype Y] [Nonempty X]
    (C : DMC X Y) :
    (∀ R : ℝ, 0 ≤ R → R < channelCapacity C → Achievable C R) ∧
    (∀ R : ℝ, Achievable C R → R ≤ channelCapacity C) := by
  sorry
