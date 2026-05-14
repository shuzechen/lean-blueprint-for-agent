import Definitions.Def_MutualInformation

/-!
# Channel capacity of a DMC

The **channel capacity** of a DMC `C : DMC X Y` is
$$C(W) \;=\; \sup_{p_X \in \Delta(X)} I(X;Y)$$
ranging over all probability mass functions on the input alphabet.

Implementation: `iSup` over the type `FinPMF X`.

`FinPMF X` is nonempty when `X` is (we can take the uniform distribution),
so the sup is well-defined; over a compact simplex with `I` continuous, the
sup is attained — that fact is packaged as the separate lemma
`channelCapacity_attained` (stated in `Theorems/Thm_capacity_attained.lean`)
rather than baked into the definition.
-/

open scoped BigOperators

/-- Channel capacity (in bits per channel use) of a discrete memoryless
    channel. -/
noncomputable def channelCapacity
    {X Y : Type*} [Fintype X] [Fintype Y] [Nonempty X]
    (C : DMC X Y) : ℝ :=
  ⨆ pX : FinPMF X, mutualInformation pX.toFun C.W
