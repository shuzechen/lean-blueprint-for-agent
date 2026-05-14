import Definitions.Def_Entropy

/-!
# Mutual information

For an input pmf `pX` on `X` and a channel `W : X → Y → ℝ`, the
**mutual information** between input and output is
$$I(X;Y) = H(Y) - H(Y \mid X) = \sum_{x,y} p_X(x)\, W(y\mid x)\,
            \log_2 \frac{W(y\mid x)}{p_Y(y)}$$
where `p_Y(y) = ∑ₓ pX(x) W(y∣x)` is the output marginal.

We define `mutualInformation` via the closed-form $H(Y) - H(Y\mid X)$ form;
the log-ratio form will be a *lemma* (`mutualInformation_eq_kl_form`), not the
definition, so that the type is unambiguously a real number even when `pX` has
zero entries. -/

open scoped BigOperators

/-- Mutual information `I(X;Y)` (in bits) for input pmf `pX` and channel `W`. -/
noncomputable def mutualInformation
    {X Y : Type*} [Fintype X] [Fintype Y]
    (pX : X → ℝ) (W : X → Y → ℝ) : ℝ :=
  entropy (outputMarginal pX W) - condEntropy pX W
