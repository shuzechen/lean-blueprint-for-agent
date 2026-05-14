import Theorems.Thm_noisy_channel_coding_theorem
import Theorems.Thm_channel_coding_achievability
import Theorems.Thm_channel_coding_converse

/-!
# Sketch — Shannon's Noisy-Channel Coding Theorem

Top-level decomposition: bundle achievability and weak converse.

This sketch is `sorry`-free; the two children
(`channel_coding_achievability`, `channel_coding_converse`) carry the `sorry`s.
-/

theorem solution
    {X Y : Type*} [Fintype X] [Fintype Y] [Nonempty X]
    (C : DMC X Y) :
    (∀ R : ℝ, 0 ≤ R → R < channelCapacity C → Achievable C R) ∧
    (∀ R : ℝ, Achievable C R → R ≤ channelCapacity C) :=
  ⟨channel_coding_achievability C, channel_coding_converse C⟩
