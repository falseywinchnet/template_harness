/-!
Logical vocabulary for statement-faithful claims.

These definitions do not prove a project theorem. They force projects to name
the admissible domain, conclusion, counterexample, objective interior, and the
initialization/preservation distinction explicitly.
-/

namespace Formal.ClaimContract

def Counterexample {α : Type} (admissible conclusion : α → Prop) (x : α) : Prop :=
  admissible x ∧ ¬ conclusion x

def Target {α : Type} (admissible conclusion : α → Prop) : Prop :=
  ∀ x, admissible x → conclusion x

def ObjectiveInterior {α : Type} (admissible conclusion : α → Prop) : Prop :=
  ∃ x, admissible x ∧ conclusion x

theorem target_excludes_counterexample {α : Type} {admissible conclusion : α → Prop}
    (target : Target admissible conclusion) :
    ¬ ∃ x, Counterexample admissible conclusion x := by
  intro ⟨x, hx, hnot⟩
  exact hnot (target x hx)

theorem target_of_no_counterexample {α : Type} {admissible conclusion : α → Prop}
    (none : ¬ ∃ x, Counterexample admissible conclusion x) :
    Target admissible conclusion := by
  intro x hx
  exact Classical.byContradiction fun hnot => none ⟨x, hx, hnot⟩

theorem target_iff_no_counterexample {α : Type} (admissible conclusion : α → Prop) :
    Target admissible conclusion ↔ ¬ ∃ x, Counterexample admissible conclusion x := by
  constructor
  · exact target_excludes_counterexample
  · exact target_of_no_counterexample

theorem objectiveInterior_of_witness {α : Type} {admissible conclusion : α → Prop}
    (x : α) (admissibleWitness : admissible x) (conclusionWitness : conclusion x) :
    ObjectiveInterior admissible conclusion := by
  exact ⟨x, admissibleWitness, conclusionWitness⟩

inductive Reachable {α : Type} (initial : α → Prop) (step : α → α → Prop) : α → Prop
  | initial {x} : initial x → Reachable initial step x
  | step {x y} : Reachable initial step x → step x y → Reachable initial step y

theorem reachable_in_target {α : Type} {initial target : α → Prop} {step : α → α → Prop}
    (initialization : ∀ x, initial x → target x)
    (preservation : ∀ x y, target x → step x y → target y) :
    ∀ x, Reachable initial step x → target x := by
  intro x reachable
  induction reachable with
  | initial hx => exact initialization _ hx
  | step reachable hstep ih => exact preservation _ _ ih hstep

end Formal.ClaimContract
