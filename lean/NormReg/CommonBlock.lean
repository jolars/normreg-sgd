import Mathlib.Data.Real.Archimedean
import NormReg.OracleLargeRates

/-!
# Increasing the common-feature dimension

This module checks `prop:common-block-dimension` in `paper/main.tex`, conditional
on the moment equations `eq:common-block-moments`. It compares both moments by
induction at the same rate and stop, then takes real infima over the same
nonnegative rates and budget-limited stops. Neither stability nor attainment of
the infimum is required. The conclusions apply separately to U and S; they do
not assert monotonicity of their risk difference.
-/

namespace NormReg

def commonBlockFactor (m : ℕ) (u : ℝ) : ℝ :=
  1 - 2 * u + (m : ℝ) * u ^ 2

lemma commonBlockFactor_eq (m : ℕ) (u : ℝ) :
    commonBlockFactor m u = (1 - u) ^ 2 + ((m : ℝ) - 1) * u ^ 2 := by
  unfold commonBlockFactor
  ring

lemma commonBlockFactor_nonneg {m : ℕ} (hm : 1 ≤ m) (u : ℝ) :
    0 ≤ commonBlockFactor m u := by
  have hm' : (1 : ℝ) ≤ (m : ℝ) := by exact_mod_cast hm
  rw [commonBlockFactor_eq]
  exact add_nonneg (sq_nonneg _) (mul_nonneg (by linarith) (sq_nonneg u))

lemma commonBlockFactor_mono {m₁ m₂ : ℕ} (hm : m₁ ≤ m₂) (u : ℝ) :
    commonBlockFactor m₁ u ≤ commonBlockFactor m₂ u := by
  have hmul := mul_le_mul_of_nonneg_right (Nat.cast_le.mpr hm : (m₁ : ℝ) ≤ m₂)
    (sq_nonneg u)
  unfold commonBlockFactor
  linarith only [hmul]

/-- The block equations retain arbitrary nonnegative observation-noise variance. -/
structure CommonBlockMomentRecurrence (m : ℕ) (b θ u ν : ℝ)
    (G H : ℕ → ℝ) : Prop where
  common : ∀ k, G (k + 1) = commonBlockFactor m u * G k +
    (m : ℝ) * u ^ 2 * (b * H k + ν)
  rare : ∀ k, H (k + 1) = rareFactor b θ * H k + b * θ ^ 2 * (G k + ν)

/-- At dimension one, the block equations recover the existing two-feature equations. -/
theorem CommonBlockMomentRecurrence.one_iff_general {b θ u ν : ℝ} {G H : ℕ → ℝ} :
    CommonBlockMomentRecurrence 1 b θ u ν G H ↔ GeneralMomentRecurrence b θ u ν G H := by
  constructor
  · intro rec
    constructor
    · intro k
      rw [rec.common k, commonBlockFactor_eq]
      norm_num
      ring
    · intro k
      rw [rec.rare k]
      ring
  · intro rec
    constructor
    · intro k
      rw [rec.common k, commonBlockFactor_eq]
      norm_num
      ring
    · intro k
      rw [rec.rare k]
      ring

lemma CommonBlockMomentRecurrence.nonneg {m : ℕ} {b θ u ν : ℝ} {G H : ℕ → ℝ}
    (rec : CommonBlockMomentRecurrence m b θ u ν G H)
    (hm : 1 ≤ m) (hb : 0 ≤ b) (hb' : b ≤ 1 / 4)
    (hν : 0 ≤ ν) (hG : 0 ≤ G 0) (hH : 0 ≤ H 0) (k : ℕ) :
    0 ≤ G k ∧ 0 ≤ H k := by
  have ha := commonBlockFactor_nonneg hm u
  have hd := rareFactor_nonneg hb hb' θ
  induction k with
  | zero => exact ⟨hG, hH⟩
  | succ k ih =>
    obtain ⟨hg, hh⟩ := ih
    constructor
    · rw [rec.common k]
      positivity
    · rw [rec.rare k]
      positivity

/-- Increasing dimension preserves coordinatewise order at every finite stop. -/
theorem CommonBlockMomentRecurrence.dimension_mono {m₁ m₂ : ℕ} {b θ u ν : ℝ}
    {G₁ H₁ G₂ H₂ : ℕ → ℝ}
    (rec₁ : CommonBlockMomentRecurrence m₁ b θ u ν G₁ H₁)
    (rec₂ : CommonBlockMomentRecurrence m₂ b θ u ν G₂ H₂)
    (hm₁ : 1 ≤ m₁) (hm : m₁ ≤ m₂) (hb : 0 ≤ b) (hb' : b ≤ 1 / 4)
    (hν : 0 ≤ ν) (hG : 0 ≤ G₁ 0) (hH : 0 ≤ H₁ 0)
    (hG₀ : G₁ 0 ≤ G₂ 0) (hH₀ : H₁ 0 ≤ H₂ 0) (k : ℕ) :
    G₁ k ≤ G₂ k ∧ H₁ k ≤ H₂ k := by
  have ha₂ := commonBlockFactor_nonneg (hm₁.trans hm) u
  have hd := rareFactor_nonneg hb hb' θ
  have hmu : (m₁ : ℝ) * u ^ 2 ≤ (m₂ : ℝ) * u ^ 2 :=
    mul_le_mul_of_nonneg_right (Nat.cast_le.mpr hm) (sq_nonneg u)
  induction k with
  | zero => exact ⟨hG₀, hH₀⟩
  | succ k ih =>
    obtain ⟨hg₁, hh₁⟩ := rec₁.nonneg hm₁ hb hb' hν hG hH k
    constructor
    · have hcommon := mul_le_mul (commonBlockFactor_mono hm u) ih.1 hg₁ ha₂
      have hforcing := mul_le_mul hmu
        (add_le_add (mul_le_mul_of_nonneg_left ih.2 hb) (le_refl ν))
        (by positivity : 0 ≤ b * H₁ k + ν)
        (by positivity : 0 ≤ (m₂ : ℝ) * u ^ 2)
      rw [rec₁.common k, rec₂.common k]
      exact add_le_add hcommon hforcing
    · rw [rec₁.rare k, rec₂.rare k]
      exact add_le_add (mul_le_mul_of_nonneg_left ih.2 hd)
        (mul_le_mul_of_nonneg_left (add_le_add ih.1 (le_refl ν)) (by positivity))

/-- Explicit trajectories make the oracle risks independent of recurrence witnesses. -/
noncomputable def commonBlockMoments (m : ℕ) (b θ u ν s r : ℝ) : ℕ → ℝ × ℝ :=
  Nat.rec (s / 4, r) fun _ p =>
    (commonBlockFactor m u * p.1 + (m : ℝ) * u ^ 2 * (b * p.2 + ν),
      rareFactor b θ * p.2 + b * θ ^ 2 * (p.1 + ν))

theorem commonBlockMoments_recurrence (m : ℕ) (b θ u ν s r : ℝ) :
    CommonBlockMomentRecurrence m b θ u ν
      (fun k => (commonBlockMoments m b θ u ν s r k).1)
      (fun k => (commonBlockMoments m b θ u ν s r k).2) :=
  ⟨fun _ => rfl, fun _ => rfl⟩

theorem commonBlockMoments_initial (m : ℕ) (b θ u ν s r : ℝ) :
    commonBlockMoments m b θ u ν s r 0 = (s / 4, r) := rfl

inductive CommonBlockScaling where
  | unscaled
  | scaled

/-- The common-coordinate step depends on the scaling, but not on dimension. -/
noncomputable def CommonBlockScaling.commonStep (A : CommonBlockScaling) (b θ : ℝ) : ℝ :=
  match A with
  | .unscaled => θ / 4
  | .scaled => b * θ

noncomputable def commonBlockRisk (A : CommonBlockScaling) (q θ ν s r : ℝ)
    (m k : ℕ) : ℝ :=
  let b := q * (1 - q)
  let p := commonBlockMoments m b θ (A.commonStep b θ) ν s r k
  rescaledRareRisk q p.1 p.2

lemma commonBlockRisk_nonneg (A : CommonBlockScaling) {q ν s r : ℝ}
    (hq : 0 ≤ q) (hq' : q ≤ 1 / 2) (hν : 0 ≤ ν) (hs : 0 ≤ s) (hr : 0 ≤ r)
    {m : ℕ} (hm : 1 ≤ m) (θ : ℝ) (k : ℕ) :
    0 ≤ commonBlockRisk A q θ ν s r m k := by
  obtain ⟨hb, hb', _, _⟩ := oracle_prevalence_bounds hq hq'
  have hG : 0 ≤ (commonBlockMoments m (q * (1 - q)) θ
      (A.commonStep (q * (1 - q)) θ) ν s r 0).1 := by
    change 0 ≤ s / 4
    positivity
  obtain ⟨hg, hh⟩ := (commonBlockMoments_recurrence m (q * (1 - q)) θ
    (A.commonStep (q * (1 - q)) θ) ν s r).nonneg hm hb hb' hν hG hr k
  unfold commonBlockRisk rescaledRareRisk
  dsimp
  positivity

/-- This is the fixed-rate part of the manuscript's dimension proposition for U and S. -/
theorem common_block_risk_dimension_mono (A : CommonBlockScaling) {q ν s r : ℝ}
    (hq : 0 ≤ q) (hq' : q ≤ 1 / 2) (hν : 0 ≤ ν) (hs : 0 ≤ s) (hr : 0 ≤ r)
    {m₁ m₂ : ℕ} (hm₁ : 1 ≤ m₁) (hm : m₁ ≤ m₂) (θ : ℝ) (k : ℕ) :
    commonBlockRisk A q θ ν s r m₁ k ≤ commonBlockRisk A q θ ν s r m₂ k := by
  obtain ⟨hb, hb', _, _⟩ := oracle_prevalence_bounds hq hq'
  have hG : 0 ≤ (commonBlockMoments m₁ (q * (1 - q)) θ
      (A.commonStep (q * (1 - q)) θ) ν s r 0).1 := by
    change 0 ≤ s / 4
    positivity
  obtain ⟨hg, hh⟩ := CommonBlockMomentRecurrence.dimension_mono
    (commonBlockMoments_recurrence m₁ (q * (1 - q)) θ
      (A.commonStep (q * (1 - q)) θ) ν s r)
    (commonBlockMoments_recurrence m₂ (q * (1 - q)) θ
      (A.commonStep (q * (1 - q)) θ) ν s r)
    hm₁ hm hb hb' hν hG hr (by rfl) (by rfl) k
  have hweight := mul_le_mul_of_nonneg_left hh (sq_nonneg (1 - q))
  unfold commonBlockRisk rescaledRareRisk
  dsimp
  linarith only [hg, hweight]

/-- A shared nonempty control set and a lower bound suffice; minimizers need not exist. -/
theorem same_controls_sInf_mono {ι : Type*} {controls : Set ι} {f g : ι → ℝ}
    (hne : controls.Nonempty) (hbelow : BddBelow (f '' controls))
    (hfg : ∀ c ∈ controls, f c ≤ g c) : sInf (f '' controls) ≤ sInf (g '' controls) := by
  apply le_csInf (hne.image g)
  rintro _ ⟨c, hc, rfl⟩
  exact (csInf_le hbelow (Set.mem_image_of_mem f hc)).trans (hfg c hc)

/-- All nonnegative constant rates and deterministic stops up to the shared budget. -/
def commonBlockControls (M : ℕ) : Set (ℝ × ℕ) :=
  {c | 0 ≤ c.1 ∧ c.2 ≤ M}

lemma commonBlockControls_nonempty (M : ℕ) : (commonBlockControls M).Nonempty :=
  ⟨(0, 0), le_rfl, Nat.zero_le M⟩

noncomputable def commonBlockOracleRisk (A : CommonBlockScaling) (q ν s r : ℝ)
    (M m : ℕ) : ℝ :=
  sInf ((fun c : ℝ × ℕ => commonBlockRisk A q c.1 ν s r m c.2) '' commonBlockControls M)

lemma commonBlockRisk_bddBelow (A : CommonBlockScaling) {q ν s r : ℝ}
    (hq : 0 ≤ q) (hq' : q ≤ 1 / 2) (hν : 0 ≤ ν) (hs : 0 ≤ s) (hr : 0 ≤ r)
    (M : ℕ) {m : ℕ} (hm : 1 ≤ m) :
    BddBelow ((fun c : ℝ × ℕ => commonBlockRisk A q c.1 ν s r m c.2) ''
      commonBlockControls M) := by
  refine ⟨0, ?_⟩
  rintro _ ⟨c, _, rfl⟩
  exact commonBlockRisk_nonneg A hq hq' hν hs hr hm c.1 c.2

/-- This is the oracle part of the dimension proposition, over the full rate domain. -/
theorem common_block_oracle_dimension_mono (A : CommonBlockScaling) {q ν s r : ℝ}
    (hq : 0 ≤ q) (hq' : q ≤ 1 / 2) (hν : 0 ≤ ν) (hs : 0 ≤ s) (hr : 0 ≤ r)
    {m₁ m₂ : ℕ} (hm₁ : 1 ≤ m₁) (hm : m₁ ≤ m₂) (M : ℕ) :
    commonBlockOracleRisk A q ν s r M m₁ ≤ commonBlockOracleRisk A q ν s r M m₂ := by
  apply same_controls_sInf_mono (commonBlockControls_nonempty M)
    (commonBlockRisk_bddBelow A hq hq' hν hs hr M hm₁)
  intro c _
  exact common_block_risk_dimension_mono A hq hq' hν hs hr hm₁ hm c.1 c.2

end NormReg
