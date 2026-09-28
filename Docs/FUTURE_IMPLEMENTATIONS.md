# Future implementations and research priorities

Status: forward-looking roadmap for the research prototype. These items are not completed results, empirical findings, or publication claims.

This roadmap follows the robustness assessment in [`Docs/THEORY_REVIEW.md`](THEORY_REVIEW.md), [`Docs/SHARED_CAPACITY_BOUND.md`](SHARED_CAPACITY_BOUND.md), [`Docs/LITERATURE_COMPARISON.md`](LITERATURE_COMPARISON.md), and [`Docs/RESEARCH_PACKAGE.md`](RESEARCH_PACKAGE.md).

## Priority 1: sharpen the shared-capacity contribution

The highest-value theoretical extension is to make the shared institutional-capacity result more distinctive and informative without turning the project into a full workforce-planning model.

### Planned work

- Define a small joint allocation problem for multiple workloads competing for the same human-capacity pool.
- Compare the current closed-form lower bound with the minimum cost of a feasible joint allocation.
- Identify conditions under which the bound is tight, loose, or uninformative.
- Add examples where individually feasible restoration plans cannot be supplied simultaneously.
- Preserve the distinction between a cost floor, an allocation optimizer, and a realized economic outcome.
- Test whether the extension changes a bound, feasible set, or comparative static relative to the closest models.

### Acceptance criteria

- A formal statement of the joint feasible set and units.
- Proofs or clearly documented derivations for any new proposition.
- Tests for tight, loose, zero-bound, and infeasible cases.
- A comparison table showing what the current bound does and does not establish.

## Priority 2: introduce optional endogenous capability dynamics

The current model treats retained capability `K` and usable human output as supplied scenario inputs. A future module may model how capability changes over time while keeping the current conditional framework intact.

### Candidate formulation

```text
K_(t+1) = K_t - delta(D_t, review_t, training_t) + g_t
```

where `delta` represents capability erosion and `g_t` represents training, re-entry, knowledge recovery, or other capacity-building flows.

### Planned work

- Keep `K_t`, productive availability, and actual human output as separate state variables.
- Specify whether erosion reflects reduced practice, weaker entry pipelines, loss of experienced workers, or organizational knowledge loss.
- Specify whether rebuilding adds company capability, institutional capacity, or both.
- Add an optional state-transition module rather than changing the baseline calculations silently.
- Include uncertainty and alternative functional forms instead of treating one erosion law as established.
- Report whether the horizon ends before capability recovery and disclose terminal states.

### Acceptance criteria

- State-transition equations with units and admissible ranges.
- Tests for no erosion, no rebuilding, full recovery, and bounded states.
- A sensitivity analysis showing which conclusions depend on the chosen dynamics.
- Clear separation between imposed dynamics and evidence-supported dynamics.

## Priority 3: validate one narrow real-world application

A bounded evidence-backed application would improve credibility more than adding many hypothetical company cases. The application should use a clearly defined workflow and comparable output and quality requirements.

### Candidate scope

- A defined software task basket;
- a specific internal business workflow;
- a regulated professional process; or
- another narrowly scoped AI-assisted production activity.

### Required evidence

- A and V: matched baseline costs and affected supplier spending.
- H: incremental cost of comparable human replacement, including productive effort and non-overlapping costs.
- Review, rework, and quality requirements.
- Immediately available human output and its capacity source.
- Qualified rival access, switching costs, and residual dependencies.
- Rebuilding expense, delay, ramp, and payment timing.
- Coverage, dates, units, and limitations for every source.

### Acceptance criteria

- Observed, calibrated, simulated, and hypothetical values are labeled separately.
- No national or industry-wide extrapolation without appropriate coverage and weights.
- Results are reported as ranges or scenarios where point identification is not defensible.
- The application reproduces the model's accounting and feasibility checks.

## Priority 4: complete the closest-literature comparison

The current literature document is a targeted checkpoint, not an exhaustive novelty review. Before making a theory contribution claim, the project should compare the candidate shared-capacity result with the nearest formal models.

### Planned work

For each closest model, record:

- state variables;
- timing and horizon;
- outside-option definition;
- adjustment or switching costs;
- capacity constraints;
- whether prices are endogenous;
- whether human-capital recovery or common-input dependence is modeled; and
- the exact result nearest to the proposed proposition.

Then map one proposed result to its nearest existing result and identify the precise additional assumption and changed conclusion.

### Acceptance criteria

- Primary sources and exact locations are recorded.
- Reading limits are explicit.
- Similar mechanisms are not relabeled as new contributions.
- The final positioning is narrowed if no distinct result survives comparison.

## Priority 5: strengthen robustness and uncertainty analysis

The existing sensitivity suite varies many assumptions one at a time. Future work should test interactions and uncertainty around the inputs that drive the conclusions most strongly.

### Planned work

- Add joint sensitivity surfaces for rebuilding cost, delay, ramp, available output, and rival eligibility.
- Separate parameter uncertainty from structural uncertainty.
- Include correlated cases where delay, rebuilding cost, and available capacity move together.
- Identify threshold reversals and no-crossing regions.
- Report partial-identification intervals when inputs are bounded rather than known.
- Add automated checks for unit consistency, duplicated costs, missing decompositions, and incompatible output definitions.
- Test numerical results against direct quarterly summation and closed-form formulas.

### Acceptance criteria

- Every sensitivity declares which inputs change and which remain fixed.
- Results include weak-effect and no-effect cases.
- Common-shock and provider-specific-shock experiments remain separate.
- No sensitivity is described as causal evidence without an identification design.

## Priority 6: extend supplier and market analysis cautiously

The current outside-option threshold measures conditional substitution discipline, not an equilibrium supplier price or monopoly outcome. A future extension may add strategic pricing, but it should remain separate from the core accounting model.

### Planned work

- Add demand response or an explicit fixed-demand limitation to any pricing module.
- Specify supplier marginal costs, fixed costs, capacity, and entry assumptions.
- Distinguish provider-specific shocks from common upstream-input shocks.
- Model multi-homing, contracts, switching frictions, and rival qualification where evidence permits.
- Compare the outside-option threshold with an explicitly defined equilibrium price problem.
- Avoid interpreting customer spending HHI as legal market concentration.

### Acceptance criteria

- A supplier-price result has an explicit demand and cost structure.
- Equilibrium conclusions are not inferred from cost crossings alone.
- Market definition and market-power claims require separate evidence.
- Fixed-demand toy results are labeled as such.

## Priority 7: preserve reproducibility and documentation

Every future extension should retain the project's current research-engineering strengths.

### Required implementation practice

- Add new modules rather than silently changing the baseline model.
- Add unit and boundary tests before adding new scenario grids.
- Freeze configurations and method documents in the run manifest.
- Record input, code, and output hashes.
- Export assumptions, provenance, units, and terminal states.
- Keep company cases separate from the independent shared-capacity illustration.
- Update the claim-to-calculation map when a new result is introduced.
- Mark unfinished work as research-in-progress rather than publication-ready.

## Suggested implementation order

1. Formalize and test the joint-capacity allocation comparison.
2. Complete the closest-model literature mapping.
3. Add uncertainty and interaction sensitivities around the shared-capacity result.
4. Build one narrow evidence-backed application.
5. Add optional endogenous capability dynamics.
6. Only then consider a separate equilibrium supplier-pricing extension.

## Explicit non-goals

These future implementations do not, by themselves, establish:

- economy-wide AI dependence;
- a causal estimate of AI-induced human-capacity erosion;
- an observed supplier markup;
- legal monopoly power or market definition;
- an optimal workforce policy;
- permanent irreversibility; or
- publication-ready originality.

The project should continue to present its central output as a conditional framework unless evidence and theory establish stronger claims.
