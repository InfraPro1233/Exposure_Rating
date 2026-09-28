# Company inputs and institutional restoration assumptions

Updated: 2026-09-27. Primary application contract; supplements
[MODEL_CONTRACT.md](../MODEL_CONTRACT.md). This is a theory/scenario framework,
not a real-company, national-capacity, or monopoly estimate.

## Research focus

Investigate how a company's dependence on an AI supplier interacts with the
cost, delay and feasibility of human substitution when productive capacity
must be reconstituted. Companies can insert their own matched internal inputs.
Use a few hypothetical examples to explain the relationships. Current model/API
prices and SWE-bench are optional software illustrations, not prerequisites.

Separate company information from institutional constraints. A firm's hiring
budget does not identify the cost or time of rebuilding education, training,
experienced-worker supply or organizational knowledge at scale. Hiring from
another covered firm may redistribute capacity without creating more of it.

## Group 1: company-owned inputs

All costs use one stated currency/cost unit and quarter. The output unit is the
company's current workload supplied by the affected AI provider; the other
production continues. No exact number of software tasks is required.

| Configuration field | Meaning and accounting rule |
| --- | --- |
| unaffected_cost_per_quarter | A: costs held unchanged across all supplied paths; exclude extra replacement labor counted below |
| incumbent_ai_spend_per_quarter | V: baseline spending affected by the particular price shock; do not shock all technology spending automatically |
| replacement_human_cost_per_quarter | H: incremental cost to replace the entire affected workload at comparable output/quality; exclude wages already counted in A |
| retained_capability | K: recoverable capability relative to a stated baseline; estimate or scenario, not raw headcount |
| immediately_replaceable_ai_output_share | r0: fraction of affected AI output humans can currently replace, net of review duties; separate from K |
| feasible_rivals | Accessible, qualified alternatives with sufficient capacity; total unshocked cost, residual incumbent spending and switching bill |
| dedicated_review_hours_available | Separate oversight budget; missing is unverified, not zero |

The application is conditioned on comparable output and quality. Task mix,
contracts, regulatory eligibility and quality requirements inform H and rival
qualification; they are not automatically identified by reported spending.
An empirical application needs definitions and evidence for these inputs.

## Group 2: institutional assumptions or externally justified ranges

- Reconstruction expense: company-facing costs or an explicitly allocated
  share of collective rebuilding, in the SAME cost unit. Do not charge a whole
  national education programme to a single firm or duplicate shared costs.
- Restoration delay and ramp: supplied quarters, not forecasts or automatic
  consequences of K. State which capacity sources can add usable output.
- Feasibility: whether the specified reconstruction path can be supplied.
  Beyond-horizon completion is different from an infeasible path.
- Provenance and coverage: population, capacity source, evidence/range and
  whether recruitment adds capacity or just reallocates existing workers.

The example cost rule F = Fmax(1-K) is hypothetical. A separately justified bill
can instead use cost_rule = supplied_total and total_reconstitution_cost.
Delay/ramp assumptions remain independent inputs, not enrollment-to-capacity
conversions. Internal company data alone cannot establish the supply response.

## Calculation

For unchanged affected workload over T quarters:

$$J_I(\theta)=\sum_{t=1}^T w_t(A+\theta V),\qquad
x(\theta)=\frac{(\theta-1)V}{A+V},$$

where w_t = (1+r)^(-t/4) under the stated annual discount rate. Relative exposure
is undefined at a zero baseline. K does not enter immediate fixed-mix exposure.

For a supplied human replacement share r_t, computed from quarter-average
availability:

$$J_H(\theta)=\sum_{t=1}^T w_t
\left[A+r_tH+\theta(1-r_t)V+f_t\right].$$

The outside-option threshold is the first theta >= 1 at which ANY feasible
path costs no more than continuing. Include partial use of retained humans
even if institutional rebuilding is infeasible; excluding it would overstate
dependence. A rebuilding path also incurs incumbent bills during delay/ramp.
Its equality root can exist before full restoration is attained.

A supposed rebuilding path that replaces no AI output before the horizon
does not count as an additional outside option merely because its costs equal
continuation. Its non-unique accounting root and quarterly diagnostics are
still reported.

Report the first outside-option threshold, the full reconstruction root, ending
states and residual incumbent spending separately. Do not label a threshold an
optimal provider price, complete independence or proof of monopoly. Rivals,
demand changes and entry can constrain pricing even with scarce human capacity.
Supplied paths are not an optimized staffing policy.

## Three illustrative cases

In [company_scenarios.json](../company_scenarios.json), all costs are normalized,
not measured dollars; all three have A=100, V=80 and H=100 per quarter.

| Case | K | r0 | Reconstruction profile | Rival |
| --- | ---: | ---: | --- | --- |
| Retained human capacity | 0.9 | 0.9 | Activation: no delay, 1-quarter ramp | None |
| Depleted capacity with a rival | 0.2 | 0 | Shortage: 4-quarter delay, 12-quarter ramp | Qualified, incumbent-independent alternative |
| Depleted capacity without a rival | 0.2 | 0 | Same shortage profile | None |

The depleted pair differs ONLY in rival availability. Immediate exposure is
identical across the three because their baseline spending is identical.
Comparing retained and depleted cases jointly varies availability and rebuilding
conditions; it does not identify an isolated or causal effect of K.

Keep the existing SWE application separate. No company cases are aggregated
into an industry estimate. Mathematical novelty and comparison with the closest
literature still require review.

## Run and review

Run scripts/run_company_model.py. Its output folder is data/processed/company_model/.
Company inputs and institutional assumptions get separate CSV tables; summaries,
price comparisons, affine coefficients and quarterly paths are also exported.
Input snapshots and hashes preserve reproducibility.

Check the three examples, then change one assumption at a time: available human
output, rebuilding expense, delay/ramp, or rival eligibility. Include weak/no
effects and no-crossing cases. Price shocks are stress tests, not predictions.

For the full illustrated workflow, run scripts/run_company_research.py; add
--plots for noninteractive source-table figures. It runs tests and the baseline,
cost, timing and other sensitivity exports against a frozen configuration.
pipeline_manifest.json records exactly which outputs belong to the run.

## Sensitivity accounting

experiment_settings declares separate capability and immediately available
output grids, plus a joint threshold surface. Do not infer a causal K effect
from the surface: the supplied rebuilding-cost rule links K to rebuilding
expense, while delay and ramp are held fixed.

Spending comparisons vary V with A and H unchanged, so total baseline cost
changes. Provider-allocation comparisons instead hold total AI spending and
non-AI cost unchanged. Output shares cannot be recovered from spending shares.
The three-provider financial spending HHI describes this customer's supplied
allocation, not market definition, market shares or monopoly evidence.

The rival residual-share sweep preserves its total baseline cost by shifting
unshocked cost into incumbent-sensitive spending. Eligibility and switching
bills are separate experiments; this linked residual-cost reparameterization
is not a claim that residual spending can change without an offset.

A common AI-price shock requires explicit decompositions:

- other_ai_spend_per_quarter is part of A, not an extra bill. In the supplied
  human paths it remains unchanged by human replacement of the affected basket.
- other_provider_ai_spend_per_quarter is part of each rival's TOTAL fixed cost
  per quarter, not an extra bill or inferred provider identity.

Both components move from fixed coefficients to the common-price slope,
preserving every path's cost at theta=1. Common-shock slopes pool all repriced
AI spending; they must not be interpreted as residual incumbent spending.
Missing decompositions are an error, not an assumption of zero. The primary
provider-specific calculator does not need these extra fields.

All sensitivity ranges remain hypothetical. Longer horizons may amortize
rebuilding costs across more replaced output, but comparisons omit terminal
values and future completion bills. A path can be feasible yet unfinished.
The outside-option threshold may bind on partial human replacement; it is not
a threshold for eliminating every future incumbent bill.

## Separate shared-capacity illustration

shared_capacity_experiment in the configuration defines independent sector
workload baskets, human effort, AI spending floors and joint capacity schedules.
It is NOT estimated or aggregated from the company cases. Its capacities use
comparable productive hours; their coverage and availability require separate
justification.

SHARED_CAPACITY_BOUND.md proves the common-price cost floor. AI spending
floors must cover every qualified route for remaining output, and the feasible
set and available capacity must not change with the price shock. Provider-
specific shocks with unshocked substitutes do not automatically satisfy this
assumption. The extension does not compute an optimal workforce policy,
institutional rebuilding expenditure, relative baseline or monopoly power.
