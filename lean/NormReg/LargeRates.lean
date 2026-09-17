import Mathlib.Data.Real.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

/-!
# Large-rate lower bounds for the predictive moment recurrence

The recurrence and risk functional are (T5) and (T4) in
`notes/predictive-theorem.md`, with noise variance normalized to one.
The conclusions are the two large-rate lower bounds in the addendum to
`notes/predictive-proof-review.md`. The probabilistic derivation of the recurrence
is outside this formalization.
-/

namespace NormReg

/-- The rare diagonal coefficient in (T5). -/
def rareFactor (b θ : ℝ) : ℝ :=
  1 - b * θ * (2 - θ + 3 * b * θ)

/-- The original-scale rare-presence risk in (T4), excluding test noise. -/
noncomputable def rareRisk (q C H : ℝ) : ℝ :=
  C / 8 + (1 - q) ^ 2 * H / 2

/-- Equation (T5) is an explicit hypothesis, rather than an axiom about SGD. -/
structure MomentRecurrence (b θ u : ℝ) (C H : ℕ → ℝ) : Prop where
  common : ∀ k, C (k + 1) = (1 - u) ^ 2 * C k + 4 * u ^ 2 * b * H k + 4 * u ^ 2
  rare : ∀ k, H (k + 1) = b * θ ^ 2 / 4 * C k + rareFactor b θ * H k + b * θ ^ 2

/-- Constructing the sequences shows that the recurrence hypotheses are satisfiable. -/
theorem momentRecurrence_exists (b θ u s r : ℝ) :
    ∃ C H : ℕ → ℝ, C 0 = s ∧ H 0 = r ∧ MomentRecurrence b θ u C H := by
  let path : ℕ → ℝ × ℝ := Nat.rec (s, r) fun _ p =>
    ((1 - u) ^ 2 * p.1 + 4 * u ^ 2 * b * p.2 + 4 * u ^ 2,
      b * θ ^ 2 / 4 * p.1 + rareFactor b θ * p.2 + b * θ ^ 2)
  exact ⟨fun k => (path k).1, fun k => (path k).2, rfl, rfl,
    ⟨fun _ => rfl, fun _ => rfl⟩⟩

lemma rareFactor_eq (b θ : ℝ) :
    rareFactor b θ = (1 - b * θ) ^ 2 + b * θ ^ 2 * (1 - 4 * b) := by
  unfold rareFactor
  ring

lemma rareFactor_nonneg {b : ℝ} (hb : 0 ≤ b) (hb' : b ≤ 1 / 4) (θ : ℝ) :
    0 ≤ rareFactor b θ := by
  rw [rareFactor_eq]
  have : 0 ≤ 1 - 4 * b := by linarith
  positivity

lemma MomentRecurrence.nonneg {b θ u : ℝ} {C H : ℕ → ℝ}
    (rec : MomentRecurrence b θ u C H) (hb : 0 ≤ b) (hb' : b ≤ 1 / 4)
    (hC : 0 ≤ C 0) (hH : 0 ≤ H 0) (k : ℕ) :
    0 ≤ C k ∧ 0 ≤ H k := by
  have hd := rareFactor_nonneg hb hb' θ
  induction k with
  | zero => exact ⟨hC, hH⟩
  | succ k ih =>
    obtain ⟨hc, hh⟩ := ih
    constructor
    · rw [rec.common k]
      positivity
    · rw [rec.rare k]
      positivity

/-- The rare-signal floor is preserved even when the rate is unstable. -/
lemma rare_floor_step {b θ : ℝ} (hb : 0 ≤ b) (hθ : 1 ≤ θ) :
    1 / (1 + 3 * b) ≤ rareFactor b θ * (1 / (1 + 3 * b)) + b * θ ^ 2 := by
  have hden : 0 < 1 + 3 * b := by positivity
  have hid : rareFactor b θ * (1 / (1 + 3 * b)) + b * θ ^ 2 -
      1 / (1 + 3 * b) = 2 * b * θ * (θ - 1) / (1 + 3 * b) := by
    unfold rareFactor
    field_simp [ne_of_gt hden]
    ring
  have hθ0 : 0 ≤ θ := by linarith
  have hθ1 : 0 ≤ θ - 1 := by linarith
  have : 0 ≤ 2 * b * θ * (θ - 1) / (1 + 3 * b) := by positivity
  linarith

theorem rare_moment_floor {b θ u : ℝ} {C H : ℕ → ℝ}
    (rec : MomentRecurrence b θ u C H) (hb : 0 ≤ b) (hb' : b ≤ 1 / 4)
    (hθ : 1 ≤ θ) (hC : 0 ≤ C 0) (hH : H 0 = 1) (k : ℕ) :
    1 / (1 + 3 * b) ≤ H k := by
  have hd := rareFactor_nonneg hb hb' θ
  have hH0 : 0 ≤ H 0 := by rw [hH]; norm_num
  induction k with
  | zero =>
    rw [hH]
    apply (div_le_iff₀ (by positivity : 0 < 1 + 3 * b)).2
    linarith
  | succ k ih =>
    have hc := (rec.nonneg hb hb' hC hH0 k).1
    have hcoupling : 0 ≤ b * θ ^ 2 / 4 * C k := by positivity
    calc
      1 / (1 + 3 * b) ≤ rareFactor b θ * (1 / (1 + 3 * b)) + b * θ ^ 2 :=
        rare_floor_step hb hθ
      _ ≤ rareFactor b θ * H k + b * θ ^ 2 :=
        add_le_add (mul_le_mul_of_nonneg_left ih hd) le_rfl
      _ ≤ H (k + 1) := by rw [rec.rare k]; linarith

lemma prevalence_bounds {q : ℝ} (hq : 0 ≤ q) (hq' : q ≤ 1 / 10000) :
    0 ≤ q * (1 - q) ∧ q * (1 - q) ≤ 1 / 4 ∧
      q * (1 - q) ≤ 1 / 10000 ∧ 2 ≤ 4 * (1 - q) ^ 2 := by
  have hq1 : 0 ≤ 1 - q := by linarith
  have hb : q * (1 - q) ≤ q := by nlinarith [sq_nonneg q]
  refine ⟨mul_nonneg hq hq1, ?_, ?_, ?_⟩
  · linarith
  · linarith
  · nlinarith [sq_nonneg q]

/-- The U lower bound in the rare-signal family, for every finite stop. -/
theorem unscaled_large_rate_lower_bound {q θ : ℝ} {C H : ℕ → ℝ}
    (hq : 0 < q) (hq' : q ≤ 1 / 10000) (hθ : 1 ≤ θ)
    (rec : MomentRecurrence (q * (1 - q)) θ (θ / 4) C H)
    (hC : 0 ≤ C 0) (hH : H 0 = 1) (k : ℕ) :
    (49 : ℝ) / 100 < rareRisk q (C k) (H k) := by
  obtain ⟨hb, hb', hbQ, _⟩ := prevalence_bounds hq.le hq'
  have hf := rare_moment_floor rec hb hb' hθ hC hH k
  have hc := (rec.nonneg hb hb' hC (by rw [hH]; norm_num) k).1
  have hden : 0 < 1 + 3 * (q * (1 - q)) := by positivity
  have hfrac : (49 : ℝ) / 100 <
      (1 - q) ^ 2 / (2 * (1 + 3 * (q * (1 - q)))) := by
    apply (lt_div_iff₀ (by positivity : 0 < 2 * (1 + 3 * (q * (1 - q))))).2
    nlinarith only [hq', hbQ, sq_nonneg q]
  have hmul := mul_le_mul_of_nonneg_left hf (sq_nonneg (1 - q))
  unfold rareRisk
  have hid : (1 - q) ^ 2 / (2 * (1 + 3 * (q * (1 - q)))) =
      (1 - q) ^ 2 * (1 / (1 + 3 * (q * (1 - q)))) / 2 := by
    field_simp [ne_of_gt hden]
  rw [hid] at hfrac
  linarith only [hfrac, hmul, hc]

/-- A weighted risk floor avoids division by the drift deficit at the boundary. -/
theorem scaled_weighted_floor {b θ w : ℝ} {C H : ℕ → ℝ}
    (rec : MomentRecurrence b θ (b * θ) C H)
    (hb : 0 ≤ b) (hb' : b ≤ 1 / 4) (hθ : 1 ≤ θ) (hw : 2 ≤ w)
    (hC : C 0 = 1) (hH : 0 ≤ H 0) (k : ℕ) :
    1 ≤ C k + w * H k := by
  have hw0 : 0 ≤ w := by linarith
  have hθ0 : 0 ≤ θ := by linarith
  have hC0 : 0 ≤ C 0 := by rw [hC]; norm_num
  have hdeficit : 0 ≤ b * θ ^ 2 * (1 - 4 * b) := by
    have : 0 ≤ 1 - 4 * b := by linarith
    positivity
  have hnoise : 1 ≤ (1 - b * θ) ^ 2 + w * (b * θ ^ 2) := by
    have hbw : 2 ≤ b + w := by linarith
    have hprod : 2 ≤ θ * (b + w) := calc
      2 ≤ b + w := hbw
      _ = 1 * (b + w) := (one_mul _).symm
      _ ≤ θ * (b + w) := mul_le_mul_of_nonneg_right hθ (by linarith)
    have : 0 ≤ b * θ * (θ * (b + w) - 2) :=
      mul_nonneg (mul_nonneg hb hθ0) (by linarith)
    nlinarith only [this]
  induction k with
  | zero => rw [hC]; nlinarith [mul_nonneg hw0 hH]
  | succ k ih =>
    obtain ⟨hc, hh⟩ := rec.nonneg hb hb' hC0 hH k
    have hfeedback : 0 ≤ 4 * (b * θ) ^ 2 * b * H k := by positivity
    have hcoupling : 0 ≤ w * (b * θ ^ 2 / 4 * C k) := by positivity
    have hextra := mul_nonneg (mul_nonneg hw0 hdeficit) hh
    have hprop := mul_le_mul_of_nonneg_left ih (sq_nonneg (1 - b * θ))
    rw [rec.common k, rec.rare k, rareFactor_eq]
    nlinarith only [hprop, hnoise, hfeedback, hcoupling, hextra, sq_nonneg (b * θ)]

/-- The S lower bound in the common-signal family, for every finite stop. -/
theorem scaled_large_rate_lower_bound {q θ : ℝ} {C H : ℕ → ℝ}
    (hq : 0 < q) (hq' : q ≤ 1 / 10000) (hθ : 1 ≤ θ)
    (rec : MomentRecurrence (q * (1 - q)) θ (q * (1 - q) * θ) C H)
    (hC : C 0 = 1) (hH : 0 ≤ H 0) (k : ℕ) :
    (1 : ℝ) / 8 ≤ rareRisk q (C k) (H k) := by
  obtain ⟨hb, hb', _, hw⟩ := prevalence_bounds hq.le hq'
  have hf := scaled_weighted_floor rec hb hb' hθ hw hC hH k
  unfold rareRisk
  linarith

end NormReg
