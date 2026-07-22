import Formal

/-!
Add `#print axioms Formal.theoremName` lines for every exported claim. Preserve
the output and exact statement comparison in the release evidence.
-/

#print axioms Formal.ClaimContract.target_iff_no_counterexample
#print axioms Formal.ClaimContract.target_excludes_counterexample
#print axioms Formal.ClaimContract.target_of_no_counterexample
#print axioms Formal.ClaimContract.objectiveInterior_of_witness
#print axioms Formal.ClaimContract.reachable_in_target
