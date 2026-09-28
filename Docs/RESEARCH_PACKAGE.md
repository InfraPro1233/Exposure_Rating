# Research package: scope, manuscript blueprint and remaining evidence

Status: mathematical/implementation handoff, not a finished academic paper.
Manuscript writing and evidence collection remain separate research work.

## 1. Research motive and question

AI-mediated production can substitute supplier bills for human production.
The important economic question is not only whether current AI production
is cheap, but which alternatives remain feasible after human productive
capacity has declined.

The paper asks how affected spending, retained capability, usable human
output, rebuilding expense/time and qualified rival access shape exposure
to supplier-price changes. Institutional constraints matter because hiring
at one organization can redistribute existing capacity without rebuilding
the capacity needed by all affected organizations.

The framework applies to firms and sectors with their own inputs. Software
benchmark data are an optional example, not a whole-economy estimate.
The independent shared-capacity illustration is not aggregated from the
hypothetical company cases.

## 2. Defensible contribution statement

Current description:

> A conditional quantitative framework separating immediate AI spending
> exposure from the cost and feasibility of human and rival-provider
> substitution, with a shared-capacity bound for common-price exposure.

The result connects individual outside-option costs to the institutional
constraint that their substitution plans must be feasible together. It
does not derive endogenous erosion, permanent lock-in, actual supplier
markups or an observed monopoly.

The affine identities and capacity bound are elementary under the stated
assumptions. They are not established as original. A theory-focused
submission still needs a precise closest-model comparison; a broader
source-supported application would need appropriate evidence.

## 3. Manuscript blueprint

| Section | Purpose | Governing artifact |
| --- | --- | --- |
| Introduction | Explain dependency, restoration and institutional rather than merely vendor-switching constraints | This package; company input contract |
| Related work | Separate established mechanisms from the candidate contribution; retain reading limits | LITERATURE_COMPARISON.md |
| Model and assumptions | Fixed comparable output/quality, common horizon, affine costs, feasible human/rival paths | MODEL_CONTRACT.md; COMPANY_INPUT_CONTRACT.md |
| Individual exposure and outside options | Exposure identity, crossing cases, sufficient capacity monotonicity, opposing spending comparative statics | THEORY_REVIEW.md |
| Institutional/shared-capacity extension | Comparable productive hours, common-input spending floor, proof, transition versus endpoint exposure | SHARED_CAPACITY_BOUND.md |
| Illustrations | Three company cases plus the separately defined shared-capacity workloads | company_scenarios.json; exported tables |
| Sensitivity and limitations | Bills paid inside horizon, timing, K versus availability, rival constraints, common shocks and omitted behaviour | Input snapshots; sensitivity tables |
| Discussion and conclusion | Conditional implications, evidence gaps, institutional resilience; no monopoly or national extrapolation | Contribution limits and checklist below |

Do not introduce new theory in the illustrative-company section. Include
the SWE application only if it clarifies calibration or a limitation;
there is no need to rerun benchmarks.

## 4. Claim selection and figures

Principal claims are the conditional results in THEORY_REVIEW.md and
SHARED_CAPACITY_BOUND.md. The former already maps claims to checks and
tables. For each manuscript claim, retain its assumptions, equation or
proof, output table, sensitivity and interpretation limit.

The generated figures show rebuilding-cost thresholds, K/availability
thresholds and adaptive exposure under different shock scopes. Every
figure should remain visibly hypothetical until externally calibrated.
The shared-capacity result is compactly represented by its three-profile
table; an additional figure is not required.

Distinguish:

- Immediate fixed-mix exposure from adaptive costs and thresholds.
- A cost equality from first weak competitiveness and actual switching.
- An accumulated transition bill from endpoint dependence.
- A cost bound from a realised outcome or statistical confidence interval.
- Customer spending allocation from legal market concentration.
- Potential weakened substitution discipline from a supplier's chosen price.

## 5. Evidence to gather, with the parameter it can justify

These are author-owned collection requirements, not completed calibration.
A theory/scenario version can retain hypothetical numbers if it says so.

| Input or claim | Evidence needed for an empirical application | Main safeguard |
| --- | --- | --- |
| A and V | Matched baseline operating costs and affected supplier spending, same scope/time | Identify what is repriced; exclude duplicated costs |
| H | Incremental productive effort and labour cost for comparable replacement output/quality | Wages alone do not identify full-workload replacement cost |
| K and initial usable share | Capability assessment and separately measured deployable productive capacity | Neither adoption, headcount nor enrolment equals capacity |
| F, delay and ramp | Recruitment, training, vacancies, knowledge recovery and productive ramp-up | Firm hiring may transfer workers rather than add collective supply |
| Institutional capacity U_t | Available productive hours, eligible skills, geography, scale and competing restoration demands | Net out review/training; prevent counting the same people twice |
| h_s | Comparable human effort for each sector's defined workload | Keep task units sector-specific; justify comparable hours |
| Common-input spending floors v_s | A justified lower floor across ALL qualified routes at stated technology/quality | One supplier bill is not a universal floor; unshocked/AI-free routes can invalidate it |
| Qualified rivals | Access, quality, capacity, contractual switching costs and residual dependencies | Do not assume technically available models are production substitutes |
| Common versus individual shocks | Explicit affected-input decomposition and conditional repricing scenarios | Do not presume prices will rise or rivals always provide protection |
| Optional C/P software ratio | Matched published success/cost records, dates and benchmark configuration | Resolution is not production acceptance; no benchmark reruns |
| Education-pipeline motivation | Actual admissions/enrolment/completion/career-entry measures with coverage and dates | A 20% headline is not a 20% capability loss or proof of AI causation |
| Originality | Direct comparison of nearest models' assumptions, timing and formal results | Four anchor papers do not establish absence of prior work |

For every source record: exact location, accessed date, reference period,
population, units, extracted value or proposition, transformation, coverage
and limitation. Keep observed, calibrated, simulated and hypothetical
quantities explicitly separate. No numerical extrapolation to the entire
economy follows without matched monetary coverage and population weights.

## 6. Reproduce the implementation

From the project root in the existing environment:

~~~powershell
.\.venv\Scripts\python.exe scripts\run_company_research.py --plots
~~~

Outputs are in data/processed/company_model/. Start with company_summary.csv,
then company_exposure.csv and shared_capacity_bound.csv. The pipeline tests
the implementation, freezes inputs/method notes and writes a manifest with
input, code and output hashes. Cost, timing and other sensitivities are
exported with their declared assumptions. The main calculation engine uses
the standard library; figures are optional.

Re-running overwrites the workflow's generated outputs, not raw observations
or source documents. Only files listed by the run manifest belong
to that run. Fixed demand, exogenous options and hypothetical institutional
supply remain assumptions even when every test passes.

## 7. Handoff and publication checklist

Implemented:

- Individual/company price exposure and feasible human/rival cost comparisons.
- Quarterly rebuilding accounting, roots, existence/feasibility and endpoint diagnostics.
- Controlled spending, capacity, provider and restoration sensitivities.
- Shared-capacity common-shock bound, proof and independent illustrations.
- Claim-to-calculation map, targeted literature comparison and reproducible exports.

Still required before a publication-ready paper:

- Author review of proofs, economic relevance and the precise closest-literature contribution.
- Any evidence required for empirical rather than hypothetical magnitudes.
- Manuscript writing, source verification, citations, final claim/figure selection and journal-specific preparation.

Completing the code and architecture does not complete these research tasks.
Do not mark the paper publishable solely because the implementation runs.
No deployment, real-company action, benchmark experiment or source-collection
campaign is implied by this handoff.
