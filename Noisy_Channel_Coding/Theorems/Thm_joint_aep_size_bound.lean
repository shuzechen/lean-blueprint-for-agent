import Theorems.Thm_joint_aep_high_probability

/-!
# Joint AEP — Property 3: cardinality bound for the typical set

$$\big|A_\varepsilon^{(n)}\big| \;\le\; 2^{\,n\,(H(X,Y) + \varepsilon)}.$$

A consequence of the lower bound on the joint pmf inside the typical set.
-/

open scoped BigOperators

/-- **Joint AEP — size bound.** The jointly-typical set has cardinality at
    most $2^{n(H(X,Y) + \varepsilon)}$. -/
theorem joint_aep_size_bound
    {X Y : Type*} [Fintype X] [Fintype Y]
    (pX : FinPMF X) (W : X → Y → ℝ)
    (hW_nonneg : ∀ x y, 0 ≤ W x y)
    (hW_sum : ∀ x, ∑ y, W x y = 1)
    (ε : ℝ) (hε : 0 < ε) (n : ℕ) :
    (jointlyTypicalSet pX.toFun W ε n).card ≤
      (2 : ℝ) ^ ((n : ℝ) *
        (entropy (fun (xy : X × Y) => jointDist pX.toFun W xy.1 xy.2) + ε)) := by
  sorry
