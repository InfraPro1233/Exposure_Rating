# AI dependence and supplier pricing model

Theory-first Python model for price exposure, human restoration, and conditional
supplier pricing. SWE-bench is a worked application, not an economy-wide estimate.
Research prototype; an academic manuscript is being developed separately.

Research question: how do retained human productive capacity, restoration
constraints and qualified alternatives affect exposure to AI supplier prices?

## Model in brief

Hold output, quality and the comparison horizon fixed. The incumbent and each
feasible alternative have costs

$$J_I(\theta)=A_I+\theta V_I,\qquad J_z(\theta)=A_z+\theta V_z.$$

Here A includes costs unaffected by the shock, V is baseline spending on the
repriced supplier, and theta is the price multiplier. Alternative paths include
human replacement or rebuilding and qualified rival providers. Restoration
costs, delays and available productive capacity determine which paths are feasible.

For unchanged production, relative price exposure is

$$x(\theta)=\frac{(\theta-1)V_I}{A_I+V_I}.$$

Hypothetical one-quarter example: A=100 and V=80 give baseline cost 180.
Doubling the affected price raises cost to 260, or 44.4%, before substitution.
The first outside-option threshold is the lowest multiplier at or above one
where a supplied feasible alternative is no more costly. It is not a supplier's
chosen price, observed markup, or proof of monopoly. Retained capability and
immediately usable human output are separate inputs.

Start with the [research package](Docs/RESEARCH_PACKAGE.md) for the motive,
manuscript blueprint, claim limits, data-collection requirements and handoff.

The primary application now uses a company's own baseline spending and a
SEPARATE group of institutional restoration assumptions. It needs no benchmark
or specific model/API prices. See [company input contract](Docs/COMPANY_INPUT_CONTRACT.md).

## Run

From the project root in PowerShell, with Python 3.12 or newer:

~~~powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe scripts\run_company_research.py
~~~

The engine and CSV runners use only the Python standard library. The three
hypothetical company cases are in [company_scenarios.json](company_scenarios.json).
The full runner tests the code, freezes the configuration, and exports all
company comparisons and sensitivity tables. Results are in
data/processed/company_model/. Review company_summary.csv first, then RESULTS.md.
The two depleted-capacity cases differ only in rival availability.

Optional figures need Matplotlib (no interactive windows):

~~~powershell
.\.venv\Scripts\python.exe -m pip install -e ".[plots]"
.\.venv\Scripts\python.exe scripts\run_company_research.py --plots
~~~

Use --config and --output to select a configuration and result folder.
--skip-tests is available when checks were run separately. The full illustrative
workflow expects the two named depleted-capacity cases; the standalone
run_company_model.py accepts other company cases without that experiment suite.
The full workflow also requires shared_capacity_experiment with capacity
schedules matching the chosen horizon. That independent illustration is
not aggregated from the company cases.

Individual steps can also be run separately. To vary only reconstruction cost
(Fmax = 0, 100, 200, 400):

~~~powershell
.\.venv\Scripts\python.exe scripts\check_reconstitution_costs.py
~~~

This exports reconstitution_cost_sensitivity.csv alongside the company results,
plus its input snapshot. It checks human roots against the analytical formula.
Fmax is the full reconstruction scale; the actual example bill is Fmax*(1-K).
Baseline configuration and company-result tables are not overwritten.

To test restoration delay, ramp and institutional feasibility separately:

~~~powershell
.\.venv\Scripts\python.exe scripts\check_reconstitution_timing.py
~~~

This exports 14 timing/feasibility rows and an input snapshot. Company spending,
capability, planned rebuilding bill and rival terms remain fixed. Partial
restoration, no usable rebuilding within the horizon, and an infeasible
institutional path are distinct outcomes. Unfinished paths include only the
rebuilding bills paid within the horizon, not future completion costs.

The separate SWE-based software example remains available in scripts/run_model.py.
For its optional noninteractive figures:

~~~powershell
.\.venv\Scripts\python.exe -m pip install -e ".[plots]"
.\.venv\Scripts\python.exe scripts\run_model.py --plots
~~~

Edit [scenarios.json](scenarios.json) for that optional software example. A different scenario
file and output folder can be supplied with --config and --output. Running the
same configuration overwrites its generated results, not the raw input data or
the earlier hand-written example scripts.

## Modules

| File | Calculation |
| --- | --- |
| company.py | Company spending and separate institutional assumptions; three-case application |
| experiments.py | Capability/availability, spending, rival, horizon and shock-scope comparisons |
| systemic.py | Analytical common-price exposure floor under shared human capacity; no allocation optimizer |
| cost.py | C/P, separate review/rework, production cost, dollar/relative exposure |
| portfolio.py | Output-weighted provider allocation, repricing, cheapest feasible model |
| threshold.py | Equal-cost roots and first outside-option threshold at prices >= 1 |
| provider.py | Revenue/profit and exact finite-path supplier price comparison |
| restoration.py | Quarterly continuation/restoration, feasibility, discounting, reversal root |

An outside-option threshold clips a baseline-competitive option to 1. Adoption
and reversal **equality roots** do not: absent, non-positive, non-unique, and
out-of-grid roots remain explicit. A restoration equality can be reached on a
partial path without completing the restoration target.

## Primary company outputs

The company runner exports company_inputs.csv and institutional_assumptions.csv
separately. company_summary.csv compares the three cases; company_exposure.csv
shows price exposure and the least-cost supplied feasible path.
company_paths.csv gives the horizon cost coefficients, and company_quarters.csv
allows reconstruction of the human paths. These are not workforce optimizations.
The manifest and input snapshot record provenance and reproducibility.

The examples use normalized cost units, not particular models' API prices.
Internal spending and capability estimates do not identify institutional supply:
rebuilding costs, timing and feasibility still require ranges or external evidence.
The affine method is general; the supplied cost/ramp rules are hypothetical.

The full runner additionally exports:

- capacity_sensitivity.csv and capacity_surface.csv: separate K from immediately
  usable human output. The heatmap outcome is an outside-option threshold, not
  immediate exposure.
- horizon_discount_sensitivity.csv: equal-output comparisons within each horizon;
  beyond-horizon rebuilding bills and terminal values are excluded.
- spending_sensitivity.csv: holds other costs fixed, so baseline total cost changes.
  Greater immediate exposure can coexist with an earlier substitution threshold.
- rival_constraints.csv: eligibility, switching bills and residual incumbent
  spending. The residual-share experiment preserves the rival's baseline total.
- shock_scope_sensitivity.csv: provider-specific versus common proportional AI
  repricing, with explicit other-provider spending.
- provider_allocation_sensitivity.csv: diversification at a fixed total AI budget.
  Spending HHI is not task allocation or legal market concentration.

experiment_settings in company_scenarios.json declares the sensitivity ranges.
The cost/timing scripts also snapshot their declared variants. These ranges are
hypothetical, not confidence intervals. pipeline_manifest.json records the
finished steps, tests, input/code/output hashes, and table row counts. Only its
listed artifacts belong to that run; older files in the folder are not refreshed
automatically. A failed workflow is marked failed rather than complete.

Three optional source-table figures are exported to figures/: rebuilding
thresholds, K/availability thresholds, and adaptive costs under different shock
scopes. These are scenario illustrations, not empirical findings.

shared_capacity_bound.csv and shared_capacity_quarters.csv additionally report
a separate hypothetical workload system with a shared productive-hours cap.
The [proved bound](Docs/SHARED_CAPACITY_BOUND.md) covers price increases and
cuts with different inequality directions. Spending floors must hold across
all qualified common-shock AI routes. A zero bound is inconclusive; a positive
horizon floor can reflect transition bills even when ending dependence is zero.
The exporter supplies no adaptive baseline or invented relative exposure.

The pipeline freezes the controlling model and method documents in
inputs/methods/ and records their hashes. This preserves the interpretation
associated with each run. Legacy briefing and planning documents are not part
of the public repository.

## Optional software-example outputs and assumptions

Results go to data/processed/model/: technology inputs, static exposure,
sector choices/thresholds, supplier profit/price solution, provider shares and
switching comparisons, quarterly restoration tables/summaries, one-at-a-time
sensitivities, and hypothetical firms. Optional figures are in its figures/.
The manifest records input/code hashes, Python version, and limitations; its
inputs/ folder snapshots the supplied CSV and configuration.

The capacity_supplier_pricing.csv table compares human-capacity states with
and without a rival. The first outside-option threshold and the supplier profit
optimum are distinct: a partial switch can leave residual supplier spending.

- The 13 local SWE-bench observations are reused as recorded. C/P is a derived
  benchmark spending ratio, not independent-retry or production-acceptance proof.
  No benchmark is rerun, and no new external sources are claimed.
- Human task cost, adoption/capability, supplier identities, outside options,
  restoration costs/times, and acceptance/review sensitivities are hypothetical.
  Model organization does not identify the actual billed/hosting supplier.
- Core software scenarios use 1,000 outputs per quarter, 20 quarters, and zero
  discounting. Initial human availability is explicitly set to initial human
  output, **not K**. Profile delays/ramps do not automatically depend on K; the
  example restoration bill alone is assumed linear in 1-K.
- Restoration availability is a quarter-average linear ramp. Capability is
  tracked separately at quarter end, with no additional erosion. Outlays are
  paid uniformly during the ramp; beyond-horizon outlays are not charged.
  A zero ramp is instantaneous at the start of the first quarter after the
  delay. Its full payment occurs that quarter. Terminal values are omitted;
  ending states, planned/paid outlays, and incomplete restoration are disclosed.
- Human availability is net of review work. A review budget must be dedicated
  separately: the same hours cannot also produce the human output. Missing
  budgets are labeled **unverified**, not physically validated. Output-shortfall
  scenarios retain diagnostic planned costs but have no valid total/root.
- Provider comparisons use each portfolio's own baseline. Common proportional
  execution shocks preserve rankings. Switching eligibility is assumed here;
  it is a frictionless bound, not proof that providers offer equivalent quality.
- Pricing assumes fixed output, exogenous paths, and constant marginal cost in
  baseline-price units, before fixed supplier costs. Ties select the first
  listed path, so weak cost competitiveness need not mean actual switching.
  Exact pairwise boundaries and one-sided profit limits are checked. An
  unattained supremum is not labeled an optimal price. Residual dependence at
  every feasible path gives unbounded profit in this fixed-demand toy model,
  **not evidence that a real supplier can charge unlimited prices**.
  price_exact and profit_exact preserve rational results; use Fraction(price_exact)
  to reconstruct exact ties rather than the rounded floating-point price.
- Pipeline sensitivities are hypothetical talent-development delays/ramps,
  not conversions of a CS-enrollment headline. They do not apply automatically
  to experienced-worker re-entry. Fractional ramp durations are rounded up to
  whole quarters. Firms A-C additionally show annual static
  scaling; D has no invented annual volume. Dynamic firm comparisons remain
  normalized per 1,000 outputs per quarter.

Run the tests before interpreting modified scenarios. The suite checks algebra,
boundary cases, exact ties, supplier maxima/suprema, unbounded cases, output/review
feasibility, ramp/payment timing, discounting, and a small end-to-end export.
This verifies implementation, not academic novelty, empirical calibration,
causal irreversibility, real monopoly, or publication readiness. The literature
comparison and source-supported restoration/human-cost inputs remain research
work; the controlling definitions are in [MODEL_CONTRACT.md](MODEL_CONTRACT.md).

The internal [theory review](Docs/THEORY_REVIEW.md) gives the affine crossing
cases, sufficient capacity-monotonicity conditions, dynamic restoration root,
opposing spending comparative statics, and shared-sector aggregation limits.
It includes a claim-to-calculation map and hand-checkable boundary tests.
A first competitive alternative is not necessarily lasting price protection;
shared institutional capacity may prevent individual sector paths being
supplied together. The review does not establish originality.

The [closest-work comparison](Docs/LITERATURE_COMPARISON.md) records four
primary references and reading limits. It separates established mechanisms
from the still-unresolved contribution. This is a targeted architecture
checkpoint, not an exhaustive literature review or publication endorsement.
