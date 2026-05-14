# Noisy_Channel_Coding — Shannon's Noisy-Channel Coding Theorem

Formalization of Shannon's 1948 Noisy-Channel Coding Theorem for **discrete memoryless
channels (DMCs)** in Lean 4, following the textbook treatment of
Cover & Thomas (*Elements of Information Theory*, 2nd ed., Ch. 7–8).

The plan in this file is the **blueprint** the user reviews before any proof work
starts. The companion LaTeX blueprint lives in `blueprint/src/content.tex` and
mirrors the Lean dependency graph exactly.

## Source

- Wikipedia: <https://en.wikipedia.org/wiki/Noisy-channel_coding_theorem>
- Cover & Thomas, *Elements of Information Theory*, 2nd ed., Theorem 7.7.1 + Theorem 7.9.1
- Shannon, "A Mathematical Theory of Communication" (1948), §13 and §15.

## Theorem (informal)

For a discrete memoryless channel with capacity
$C = \sup_{p_X} I(X;Y)$:

- **(Achievability)** For every rate $R < C$ and every $\varepsilon > 0$, there exists
  $n_0$ such that for all $n \ge n_0$ there is a $(2^{\lceil nR \rceil}, n)$ code
  whose maximum probability of decoding error is $\le \varepsilon$.
- **(Weak converse)** Any sequence of $(2^{nR}, n)$ codes with maximum probability
  of error tending to $0$ must satisfy $R \le C$.

## Decomposition strategy

We follow Cover & Thomas's two-stage argument:

```
Thm_noisy_channel_coding_theorem    (TOP — bi-conditional R<C ↔ achievable)
  │
  ├── Thm_channel_coding_achievability   (achievability direction)
  │     │
  │     ├── Thm_random_coding_expected_error   (jointly-typical decoding)
  │     │     │
  │     │     ├── Thm_joint_aep_high_probability
  │     │     ├── Thm_joint_aep_independent_pair_bound
  │     │     └── Thm_joint_aep_size_bound
  │     │           (all three follow from)
  │     │             └── Thm_aep_weak_law   (Shannon-McMillan, weak form)
  │     │
  │     └── Thm_expurgation_max_from_average
  │
  └── Thm_channel_coding_converse        (weak converse, R > C ⇒ P_e ↛ 0)
        │
        ├── Thm_fano_inequality
        ├── Thm_mutual_info_dmc_le_n_capacity     (chain rule + memoryless)
        └── Thm_data_processing_inequality_codeword
```

The top-level sketch `Sketches/sketch_noisy_channel_coding.lean` will combine
`Thm_channel_coding_achievability` and `Thm_channel_coding_converse` into a
`sorry`-free proof of `Thm_noisy_channel_coding_theorem`. All deeper layers are
deferred (each is a sub-blueprint of its own).

## Definitions uploaded to the platform

Every entity appearing in any **statement** of a Lemma/Theorem above must be a
shared definition. Proof-machinery (random codebooks, typical sets used only
inside achievability) lives in `Theorems/` files or inline in sketches —
**not** in `Definitions/`.

- `Def_DMC` — `DMC X Y`: input/output finite alphabets and a stochastic
  transition matrix $W(y\mid x)$. Also `DMC.product`: the $n$-fold extension
  $W^n(y^n \mid x^n) = \prod_i W(y_i \mid x_i)$.
- `Def_Entropy` — Shannon entropy `H(p)` of a discrete distribution.
  Conditional entropy `H(Y|X)` over a joint distribution.
- `Def_MutualInformation` — `I(X;Y)` as `H(Y) - H(Y|X)`, defined from the
  joint distribution induced by an input pmf $p_X$ and channel $W$.
- `Def_ChannelCapacity` — `C(W) = sup_{p_X} I(X;Y)`. We use `iSup` over the
  compact set of input pmfs; the sup is attained because the simplex is compact
  and $I$ is continuous (we package this as an existence lemma rather than as
  part of the definition, to avoid `sInf`/`sSup` fallback pitfalls).
- `Def_Code` — `Code W M n`: an encoder `Fin M → (Fin n → X)` and a decoder
  `(Fin n → Y) → Fin M`. Error probabilities `Code.errorPr i`, `Code.avgError`,
  `Code.maxError`.
- `Def_AchievableRate` — `Achievable W R`: there exists a sequence of
  $(\lceil 2^{nR} \rceil, n)$ codes whose max error tends to $0$.

`Def_TypicalSet`, `Def_JointlyTypicalSet`, and the random-codebook construction
are proof machinery for `Thm_random_coding_expected_error` only; they remain
inside `Theorems/` and `Sketches/` rather than `Definitions/`.

## Decomposition decisions made up front

- **Rates are real numbers**, not rationals. $R$ is a real $\ge 0$; the code
  size is $M_n = \lceil 2^{nR} \rceil$ so that $\log_2 M_n / n \to R$. The
  alternative (`M : ℕ`, $R := \log_2 M / n$) makes the achievability statement
  uglier and ties the rate to the chosen $n$.
- **`maxError`, not `avgError`** in the top-level statement of achievability.
  Average is easier to bound from random coding; max is what users want.
  The bridge is `Thm_expurgation_max_from_average`.
- **Discrete memoryless channels only.** No continuous channels (Gaussian etc.)
  — those are a separate project.
- **Base-2 logarithms** in entropy, so rate is measured in bits per channel
  use. Lean-wise we use `Real.logb 2`.
- **Sup attained** is part of `Def_ChannelCapacity`'s API (a separate lemma
  `channelCapacity_attained`), not inlined into the `iSup`. This keeps the
  definition computationally well-behaved and avoids `sSup`-on-empty pitfalls.
- **Converse is the *weak* converse.** Wolfowitz's strong converse is deferred
  to a future project.

## Local testing

```bash
cd ~/LeanWorkspace/Noisy_Channel_Coding
lake env lean Definitions/Def_DMC.lean         # type-check a single file
lake build                                     # build everything
```

`mathlib4` is shared via the parent-directory path-dep.

## Deferred (future iterations)

- Proofs of every leaf in the dependency tree (each is `sorry` for now).
- Level-2 decomposition of `Thm_random_coding_expected_error` (its sketch
  bridging the three joint-AEP lemmas).
- Wolfowitz's strong converse $P_e \ge 1 - e^{-n\alpha(R-C)}$.
- Continuous/Gaussian channels and bandwidth-limited Shannon-Hartley theorem.

## Design principle: definitions must be clear, correct, and consistent

When introducing a new `Definitions/Def_*.lean`, avoid constructions that
silently return a meaningless value in pathological cases (`sInf` on empty,
`sSup` on unbounded, `Nat.find` without a witness). For `channelCapacity`
we use a `noncomputable iSup` over the simplex of input pmfs and **pair it
with a separate `attained` lemma** rather than building attainment into the
definition. Budget up to ~100 Lean lines per Definition file for inlined
existence/finiteness proofs; flag larger constructions before falling back.
