import NormReg.CommonBlock

/-!
The expected axiom lists make incomplete dependencies and additional axioms fail
the build, including when the main theorem itself contains no placeholder.
-/

/--
info: 'NormReg.momentRecurrence_exists' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms NormReg.momentRecurrence_exists

/--
info: 'NormReg.unscaled_large_rate_lower_bound' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms NormReg.unscaled_large_rate_lower_bound

/--
info: 'NormReg.unscaled_small_prevalence_lower_bound' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms NormReg.unscaled_small_prevalence_lower_bound

/--
info: 'NormReg.scaled_large_rate_lower_bound' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms NormReg.scaled_large_rate_lower_bound

/--
info: 'NormReg.MomentRecurrence.toGeneral' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms NormReg.MomentRecurrence.toGeneral

/--
info: 'NormReg.rescaledRareRisk_eq' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms NormReg.rescaledRareRisk_eq

/--
info: 'NormReg.generalMomentRecurrence_exists' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms NormReg.generalMomentRecurrence_exists

/--
info: 'NormReg.oracle_unscaled_geometric_lower_bound' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms NormReg.oracle_unscaled_geometric_lower_bound

/--
info: 'NormReg.oracle_scaled_geometric_lower_bound' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms NormReg.oracle_scaled_geometric_lower_bound

/--
info: 'NormReg.oracle_unscaled_large_rate_lower_bound' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms NormReg.oracle_unscaled_large_rate_lower_bound

/--
info: 'NormReg.oracle_scaled_large_rate_lower_bound' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms NormReg.oracle_scaled_large_rate_lower_bound

/--
info: 'NormReg.oracle_rate_cutoff_bounds' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms NormReg.oracle_rate_cutoff_bounds

/--
info: 'NormReg.CommonBlockMomentRecurrence.one_iff_general' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms NormReg.CommonBlockMomentRecurrence.one_iff_general

/--
info: 'NormReg.commonBlockMoments_recurrence' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms NormReg.commonBlockMoments_recurrence

/--
info: 'NormReg.CommonBlockMomentRecurrence.dimension_mono' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms NormReg.CommonBlockMomentRecurrence.dimension_mono

/--
info: 'NormReg.common_block_risk_dimension_mono' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms NormReg.common_block_risk_dimension_mono

/--
info: 'NormReg.same_controls_sInf_mono' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms NormReg.same_controls_sInf_mono

/--
info: 'NormReg.common_block_oracle_dimension_mono' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms NormReg.common_block_oracle_dimension_mono
