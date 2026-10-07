import NormReg.OracleLargeRates

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
