import Mathlib.Algebra.Ring.GeomSum
import NormReg.LargeRates

/-!
# General large-rate bounds for the limiting oracle proof

The recurrence is `eq:limit-moments` in `paper/oracle-proofs.tex`, with the
rescaled common moment G = C / 4 and arbitrary noise variance ν. These proofs
check the geometric lower bounds and the rate cutoffs used to restrict the
unbounded oracle search. The parameter θ is the manuscript's rare-coordinate
step α. The derivation from SGD and the limiting approximations remain outside
this formalization.
-/

namespace NormReg

structure GeneralMomentRecurrence (b θ u ν : ℝ) (G H : ℕ → ℝ) : Prop where
  common : ∀ k, G (k + 1) = (1 - u) ^ 2 * G k + u ^ 2 * b * H k + u ^ 2 * ν
  rare : ∀ k, H (k + 1) = b * θ ^ 2 * G k + rareFactor b θ * H k + b * θ ^ 2 * ν

noncomputable def rescaledRareRisk (q G H : ℝ) : ℝ :=
  (G + (1 - q) ^ 2 * H) / 2

lemma rescaledRareRisk_eq (q G H : ℝ) :
    rescaledRareRisk q G H = rareRisk q (4 * G) H := by
  unfold rescaledRareRisk rareRisk
  ring

/-- The variance-one recurrence agrees with the manuscript's rescaled moments. -/
theorem MomentRecurrence.toGeneral {b θ u : ℝ} {C H : ℕ → ℝ}
    (rec : MomentRecurrence b θ u C H) :
    GeneralMomentRecurrence b θ u 1 (fun k => C k / 4) H := by
  constructor
  · intro k
    dsimp
    rw [rec.common k]
    ring
  · intro k
    rw [rec.rare k]
    ring

/-- The recurrence hypotheses admit sequences for every choice of parameters. -/
theorem generalMomentRecurrence_exists (b θ u ν g r : ℝ) :
    ∃ G H : ℕ → ℝ, G 0 = g ∧ H 0 = r ∧ GeneralMomentRecurrence b θ u ν G H := by
  let path : ℕ → ℝ × ℝ := Nat.rec (g, r) fun _ p =>
    ((1 - u) ^ 2 * p.1 + u ^ 2 * b * p.2 + u ^ 2 * ν,
      b * θ ^ 2 * p.1 + rareFactor b θ * p.2 + b * θ ^ 2 * ν)
  exact ⟨fun k => (path k).1, fun k => (path k).2, rfl, rfl,
    ⟨fun _ => rfl, fun _ => rfl⟩⟩

lemma GeneralMomentRecurrence.nonneg {b θ u ν : ℝ} {G H : ℕ → ℝ}
    (rec : GeneralMomentRecurrence b θ u ν G H) (hb : 0 ≤ b) (hb' : b ≤ 1 / 4)
    (hν : 0 ≤ ν) (hG : 0 ≤ G 0) (hH : 0 ≤ H 0) (k : ℕ) :
    0 ≤ G k ∧ 0 ≤ H k := by
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

/-- Finite sums cover drift factor one without dividing by a drift deficit. -/
lemma affine_geometric_lower_bound {a c : ℝ} {X : ℕ → ℝ}
    (ha : 0 ≤ a) (hstep : ∀ k, a * X k + c ≤ X (k + 1)) (k : ℕ) :
    a ^ k * X 0 + c * ∑ j ∈ Finset.range k, a ^ j ≤ X k := by
  induction k with
  | zero => simp
  | succ k ih =>
    calc
      a ^ (k + 1) * X 0 + c * ∑ j ∈ Finset.range (k + 1), a ^ j =
          a * (a ^ k * X 0 + c * ∑ j ∈ Finset.range k, a ^ j) + c := by
        rw [pow_succ, geom_sum_succ]
        ring
      _ ≤ a * X k + c := add_le_add (mul_le_mul_of_nonneg_left ih ha) le_rfl
      _ ≤ X (k + 1) := hstep k

def scaledSumFactor (b θ : ℝ) : ℝ :=
  1 - 2 * b * θ + b * θ ^ 2 * (1 - 3 * b + b ^ 2)

lemma scaledSumFactor_eq (b θ : ℝ) :
    scaledSumFactor b θ = rareFactor b θ + b ^ 3 * θ ^ 2 := by
  unfold scaledSumFactor rareFactor
  ring

lemma scaledSumFactor_nonneg {b : ℝ} (hb : 0 ≤ b) (hb' : b ≤ 1 / 4) (θ : ℝ) :
    0 ≤ scaledSumFactor b θ := by
  rw [scaledSumFactor_eq]
  have hd := rareFactor_nonneg hb hb' θ
  positivity

lemma GeneralMomentRecurrence.rare_geometric_bound {b θ u ν : ℝ} {G H : ℕ → ℝ}
    (rec : GeneralMomentRecurrence b θ u ν G H) (hb : 0 ≤ b) (hb' : b ≤ 1 / 4)
    (hν : 0 ≤ ν) (hG : 0 ≤ G 0) (hH : 0 ≤ H 0) (k : ℕ) :
    rareFactor b θ ^ k * H 0 + b * θ ^ 2 * ν *
      ∑ j ∈ Finset.range k, rareFactor b θ ^ j ≤ H k := by
  apply affine_geometric_lower_bound (rareFactor_nonneg hb hb' θ)
  intro j
  have hg := (rec.nonneg hb hb' hν hG hH j).1
  have hcoupling : 0 ≤ b * θ ^ 2 * G j := by positivity
  rw [rec.rare j]
  linarith

lemma GeneralMomentRecurrence.scaled_sum_step {b θ ν : ℝ} {G H : ℕ → ℝ}
    (rec : GeneralMomentRecurrence b θ (b * θ) ν G H)
    (hb : 0 ≤ b) (hb' : b ≤ 1 / 4)
    (hν : 0 ≤ ν) (hG : 0 ≤ G 0) (hH : 0 ≤ H 0) (k : ℕ) :
    scaledSumFactor b θ * (G k + H k) + b * θ ^ 2 * ν ≤ G (k + 1) + H (k + 1) := by
  have hg := (rec.nonneg hb hb' hν hG hH k).1
  have hdeficit : 0 ≤ b ^ 2 * θ ^ 2 * (4 - b) * G k := by
    have : 0 ≤ 4 - b := by linarith
    positivity
  have hnoise : 0 ≤ b ^ 2 * θ ^ 2 * ν := by positivity
  have hid : G (k + 1) + H (k + 1) =
      scaledSumFactor b θ * (G k + H k) + b * θ ^ 2 * ν +
        b ^ 2 * θ ^ 2 * (4 - b) * G k + b ^ 2 * θ ^ 2 * ν := by
    rw [rec.common k, rec.rare k]
    unfold scaledSumFactor rareFactor
    ring
  linarith only [hid, hdeficit, hnoise]

lemma GeneralMomentRecurrence.scaled_geometric_bound {b θ ν : ℝ} {G H : ℕ → ℝ}
    (rec : GeneralMomentRecurrence b θ (b * θ) ν G H)
    (hb : 0 ≤ b) (hb' : b ≤ 1 / 4)
    (hν : 0 ≤ ν) (hG : 0 ≤ G 0) (hH : 0 ≤ H 0) (k : ℕ) :
    scaledSumFactor b θ ^ k * (G 0 + H 0) + b * θ ^ 2 * ν *
      ∑ j ∈ Finset.range k, scaledSumFactor b θ ^ j ≤ G k + H k := by
  exact affine_geometric_lower_bound (scaledSumFactor_nonneg hb hb' θ)
    (rec.scaled_sum_step hb hb' hν hG hH) k

lemma oracle_prevalence_bounds {q : ℝ} (hq : 0 ≤ q) (hq' : q ≤ 1 / 2) :
    0 ≤ q * (1 - q) ∧ q * (1 - q) ≤ 1 / 4 ∧
      (1 - q) ^ 2 ≤ 1 ∧ 1 - (1 - q) ^ 2 ≤ 4 * (q * (1 - q)) := by
  have hq1 : 0 ≤ 1 - q := by linarith
  refine ⟨mul_nonneg hq hq1, ?_, ?_, ?_⟩
  · nlinarith [sq_nonneg (q - 1 / 2)]
  · nlinarith
  · nlinarith

theorem oracle_unscaled_geometric_lower_bound {q θ ν : ℝ} {G H : ℕ → ℝ}
    (hq : 0 < q) (hq' : q ≤ 1 / 2)
    (rec : GeneralMomentRecurrence (q * (1 - q)) θ (θ / 4) ν G H)
    (hν : 0 ≤ ν) (hG : 0 ≤ G 0) (hH : 0 ≤ H 0) (k : ℕ) :
    (1 - q) ^ 2 / 2 * (rareFactor (q * (1 - q)) θ ^ k * H 0 +
      q * (1 - q) * θ ^ 2 * ν * ∑ j ∈ Finset.range k,
        rareFactor (q * (1 - q)) θ ^ j) ≤ rescaledRareRisk q (G k) (H k) := by
  obtain ⟨hb, hb', _, _⟩ := oracle_prevalence_bounds hq.le hq'
  have hf := rec.rare_geometric_bound hb hb' hν hG hH k
  have hg := (rec.nonneg hb hb' hν hG hH k).1
  have hmul := mul_le_mul_of_nonneg_left hf (sq_nonneg (1 - q))
  unfold rescaledRareRisk
  nlinarith only [hmul, hg]

theorem oracle_scaled_geometric_lower_bound {q θ ν : ℝ} {G H : ℕ → ℝ}
    (hq : 0 < q) (hq' : q ≤ 1 / 2)
    (rec : GeneralMomentRecurrence (q * (1 - q)) θ (q * (1 - q) * θ) ν G H)
    (hν : 0 ≤ ν) (hG : 0 ≤ G 0) (hH : 0 ≤ H 0) (k : ℕ) :
    (1 - q) ^ 2 / 2 * (scaledSumFactor (q * (1 - q)) θ ^ k * (G 0 + H 0) +
      q * (1 - q) * θ ^ 2 * ν * ∑ j ∈ Finset.range k,
        scaledSumFactor (q * (1 - q)) θ ^ j) ≤ rescaledRareRisk q (G k) (H k) := by
  obtain ⟨hb, hb', hw, _⟩ := oracle_prevalence_bounds hq.le hq'
  have hf := rec.scaled_geometric_bound hb hb' hν hG hH k
  have hg := (rec.nonneg hb hb' hν hG hH k).1
  have hweight : 0 ≤ (1 - (1 - q) ^ 2) * G k :=
    mul_nonneg (by linarith) hg
  have hmul := mul_le_mul_of_nonneg_left hf (sq_nonneg (1 - q))
  unfold rescaledRareRisk
  nlinarith only [hmul, hweight]

noncomputable def unscaledRateCutoff (b : ℝ) : ℝ := 2 / (1 - 3 * b)

noncomputable def scaledRateCutoff (b : ℝ) : ℝ := 2 / (1 - 3 * b + b ^ 2)

lemma rate_cutoff_bounds {b : ℝ} (hb : 0 ≤ b) (hb' : b ≤ 1 / 16) :
    2 ≤ scaledRateCutoff b ∧ scaledRateCutoff b ≤ unscaledRateCutoff b ∧
      unscaledRateCutoff b < 3 := by
  have hdenU : 0 < 1 - 3 * b := by linarith
  have hdenS : 0 < 1 - 3 * b + b ^ 2 := by nlinarith [sq_nonneg b]
  unfold scaledRateCutoff unscaledRateCutoff
  refine ⟨?_, ?_, ?_⟩
  · apply (le_div_iff₀ hdenS).2
    nlinarith [mul_nonneg hb (by linarith : 0 ≤ 3 - b)]
  · apply (div_le_div_iff₀ hdenS hdenU).2
    nlinarith [sq_nonneg b]
  · apply (div_lt_iff₀ hdenU).2
    linarith

/-- Small prevalence places both cutoffs in a fixed compact interval. -/
theorem oracle_rate_cutoff_bounds {q : ℝ} (hq : 0 ≤ q) (hq' : q ≤ 1 / 16) :
    2 ≤ scaledRateCutoff (q * (1 - q)) ∧
      scaledRateCutoff (q * (1 - q)) ≤ unscaledRateCutoff (q * (1 - q)) ∧
      unscaledRateCutoff (q * (1 - q)) < 3 ∧
      1 - (1 - q) ^ 2 ≤ 4 * (q * (1 - q)) := by
  obtain ⟨hb, _, _, hw⟩ := oracle_prevalence_bounds hq (by linarith)
  have hb' : q * (1 - q) ≤ 1 / 16 := by nlinarith [sq_nonneg q]
  obtain ⟨hS, hSU, hU⟩ := rate_cutoff_bounds hb hb'
  exact ⟨hS, hSU, hU, hw⟩

lemma rareFactor_ge_one {b θ : ℝ} (hb : 0 ≤ b) (hb' : b ≤ 1 / 4)
    (hθ : unscaledRateCutoff b ≤ θ) : 1 ≤ rareFactor b θ := by
  have hden : 0 < 1 - 3 * b := by linarith
  have hθ0 : 0 ≤ θ := le_trans (by unfold unscaledRateCutoff; positivity) hθ
  have hprod : 2 ≤ θ * (1 - 3 * b) := (div_le_iff₀ hden).1 hθ
  have hnonneg := mul_nonneg (mul_nonneg hb hθ0) (by linarith : 0 ≤ θ * (1 - 3 * b) - 2)
  unfold rareFactor
  nlinarith only [hnonneg]

lemma scaledSumFactor_ge_one {b θ : ℝ} (hb : 0 ≤ b) (hb' : b ≤ 1 / 4)
    (hθ : scaledRateCutoff b ≤ θ) : 1 ≤ scaledSumFactor b θ := by
  have hden : 0 < 1 - 3 * b + b ^ 2 := by nlinarith [sq_nonneg b]
  have hθ0 : 0 ≤ θ := le_trans (by unfold scaledRateCutoff; positivity) hθ
  have hprod : 2 ≤ θ * (1 - 3 * b + b ^ 2) := (div_le_iff₀ hden).1 hθ
  have hnonneg := mul_nonneg (mul_nonneg hb hθ0)
    (by linarith : 0 ≤ θ * (1 - 3 * b + b ^ 2) - 2)
  unfold scaledSumFactor
  nlinarith only [hnonneg]

/-- A drift factor at least one preserves the initial moment at every stop. -/
lemma affine_initial_floor {a c : ℝ} {X : ℕ → ℝ}
    (ha : 1 ≤ a) (hc : 0 ≤ c) (hX : 0 ≤ X 0)
    (hstep : ∀ k, a * X k + c ≤ X (k + 1)) (k : ℕ) : X 0 ≤ X k := by
  induction k with
  | zero => exact le_rfl
  | succ k ih =>
    have hmul := mul_le_mul_of_nonneg_left ha (le_trans hX ih)
    have hs := hstep k
    nlinarith only [ih, hmul, hs, hc]

theorem oracle_unscaled_large_rate_lower_bound {q θ ν : ℝ} {G H : ℕ → ℝ}
    (hq : 0 < q) (hq' : q ≤ 1 / 2)
    (hθ : unscaledRateCutoff (q * (1 - q)) ≤ θ)
    (rec : GeneralMomentRecurrence (q * (1 - q)) θ (θ / 4) ν G H)
    (hν : 0 ≤ ν) (hG : 0 ≤ G 0) (hH : 0 ≤ H 0) (k : ℕ) :
    (1 - q) ^ 2 * H 0 / 2 ≤ rescaledRareRisk q (G k) (H k) := by
  obtain ⟨hb, hb', _, _⟩ := oracle_prevalence_bounds hq.le hq'
  have hf : H 0 ≤ H k := by
    apply affine_initial_floor (rareFactor_ge_one hb hb' hθ)
      (by positivity : 0 ≤ q * (1 - q) * θ ^ 2 * ν) hH
    intro j
    have hg := (rec.nonneg hb hb' hν hG hH j).1
    have hcoupling : 0 ≤ q * (1 - q) * θ ^ 2 * G j := by positivity
    rw [rec.rare j]
    linarith
  have hg := (rec.nonneg hb hb' hν hG hH k).1
  have hmul := mul_le_mul_of_nonneg_left hf (sq_nonneg (1 - q))
  unfold rescaledRareRisk
  linarith only [hmul, hg]

theorem oracle_scaled_large_rate_lower_bound {q θ ν : ℝ} {G H : ℕ → ℝ}
    (hq : 0 < q) (hq' : q ≤ 1 / 2)
    (hθ : scaledRateCutoff (q * (1 - q)) ≤ θ)
    (rec : GeneralMomentRecurrence (q * (1 - q)) θ (q * (1 - q) * θ) ν G H)
    (hν : 0 ≤ ν) (hG : 0 ≤ G 0) (hH : 0 ≤ H 0) (k : ℕ) :
    (1 - q) ^ 2 * (G 0 + H 0) / 2 ≤ rescaledRareRisk q (G k) (H k) := by
  obtain ⟨hb, hb', hw, _⟩ := oracle_prevalence_bounds hq.le hq'
  have hf := affine_initial_floor (scaledSumFactor_ge_one hb hb' hθ)
    (by positivity : 0 ≤ q * (1 - q) * θ ^ 2 * ν) (add_nonneg hG hH)
    (rec.scaled_sum_step hb hb' hν hG hH) k
  have hg := (rec.nonneg hb hb' hν hG hH k).1
  have hweight : 0 ≤ (1 - (1 - q) ^ 2) * G k :=
    mul_nonneg (by linarith) hg
  have hmul := mul_le_mul_of_nonneg_left hf (sq_nonneg (1 - q))
  unfold rescaledRareRisk
  nlinarith only [hmul, hweight]

end NormReg
