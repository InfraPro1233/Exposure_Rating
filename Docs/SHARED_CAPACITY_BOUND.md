# Conditional systemic exposure under shared human-restoration capacity

Status: derived result and tested analytical bound. This is not a manuscript,
originality claim, workforce optimizer or estimate of economy-wide monopoly.
See THEORY_REVIEW.md for the existing affine framework.

## 1. Why this belongs in the research question

Individual organizations can have plausible human-restoration plans while
the institutions supplying workers, training and knowledge recovery cannot
support all those plans simultaneously. An AI vendor alternative may also
remain exposed to the same repriced upstream input.

This result bounds unavoidable COMMON-price cost exposure under an explicitly
shared human-capacity limit. It does not assert that such a limit or shock
exists at a particular magnitude in the real economy.

## 2. Assumptions and compatible units

For each sector workload s and quarter t, define:

- h_s > 0: comparable productive human hours needed to replace its full
  affected workload, net of oversight and training commitments.
- v_s >= 0: a lower bound on the baseline-price spending on the shocked AI
  input required by ANY qualified AI route for that entire workload.
- r_st in [0,1]: share of the sector's affected output replaced by humans.
- U_t >= 0: total productive human hours available jointly for these workloads.

Each sector keeps its OWN output unit. Do not sum hospital tasks with finance
tasks. Productive hours must be genuinely comparable; any occupational or
geographic restrictions remain additional constraints. A pooled hours cap
can relax those restrictions and therefore give a conservative bound.

All covered human production obeys:

$$
\sum_s h_s r_{st}\leq U_t.
$$

Each feasible route's shocked-input spending at baseline prices is at least
v_s(1-r_st). This requires a proportional floor for remaining output, not
just an observed bill for one configuration.

Fix output, quality, technology, horizon, coverage and the joint feasible
path set independently of theta. Use the same positive price multiplier for
the input in ALL qualified AI alternatives. Financial costs use one unit.
Let each complete supplied path cost J_z(theta)=A_z+theta V_z, where A includes
unshocked human and rebuilding costs, and V pools discounted shocked-input
spending. Demand withdrawal, new technology and new entrants are outside
this conditional comparison.

This common shock is distinct from an incumbent-only shock. An unshocked
qualified rival with no exposure to this input can invalidate a positive
v_s assumption. An AI-free alternative outside the covered human-capacity
constraint would also have to be incorporated before applying the bound.

## 3. Proposition: shared-capacity residual spending floor

Let:

$$
H=\sum_s h_s,\quad B=\sum_s v_s,\quad
\lambda_{\min}=\min_s(v_s/h_s),\quad
\lambda_{\max}=\max_s(v_s/h_s).
$$

Then every jointly feasible path has quarterly shocked-input spending at
least:

$$
b_t=\max\left\{0,\ B-\lambda_{\max}U_t,\
\lambda_{\min}(H-U_t)\right\}.
$$

With quarter weights w_t=(1+d)^(-t/4), its horizon coefficient satisfies:

$$
V_z\geq\beta=\sum_t w_t b_t.
$$

### Proof

Actual remaining AI spending is at least
sum_s v_s(1-r_st). First, the avoided amount is bounded above by
sum_s lambda_max h_s r_st <= lambda_max U_t. This gives the bound
B-lambda_max U_t.

Second, remaining spending is at least
lambda_min sum_s h_s(1-r_st) >= lambda_min(H-U_t).
Spending is nonnegative. Taking the maximum of the three valid lower bounds
gives b_t. Multiply by nonnegative discount weights and sum to obtain beta.
No allocation is solved or recommended.

When lambda_min>0 and U_t<H, b_t is positive. With zero-price or unshocked
alternatives, a positive shortage need not give a positive spending floor.
The bound may be loose; a zero bound does not demonstrate zero actual exposure.

## 4. Corollary: minimum feasible cost still responds to a common shock

For a fixed nonempty finite feasible set, let:

$$
J^*(\theta)=\min_z\{A_z+\theta V_z\}.
$$

For theta_2 >= theta_1 > 0:

$$
J^*(\theta_2)-J^*(\theta_1)\geq
(\theta_2-\theta_1)\beta.
$$

### Proof

Every path satisfies
J_z(theta_2) >= J_z(theta_1)+(theta_2-theta_1)beta.
Taking minima on both sides preserves the inequality. Thus even switching
among all qualified supplied paths cannot remove this component of exposure.

For a price cut, reverse the ordered comparison:

$$
J^*(\theta_2)-J^*(\theta_1)\leq
(\theta_2-\theta_1)\beta,\qquad 0<\theta_2<\theta_1.
$$

This is an upper bound on a negative change: at least that much saving,
not a lower bound on cost increases. A zero price change gives exactly zero.
Relative bounds can divide by a positive, matched J*(theta_1) only when that
baseline is actually known. The exporter does not invent it.

### An attainable special case

For one workload, h=10, v=100 and U=5 give b=50. Consider two supplied
paths: continuation (A,V)=(20,100) and partial retained-human replacement
(20,50). Retained labour is already included in A in this witness; this does
not assert zero wages or change the main company assumptions.

The partial path is cheapest for every positive theta, so J*(theta)=20+50theta.
Every increase or cut attains the bound exactly. Thus the bound can be sharp
within its stated class, although it need not be sharp for a particular
heterogeneous system or when higher-cost human paths do not bind.

## 5. Connection to K, institutional rebuilding and reversibility

For fixed h_s and v_s, each component of b_t is nonincreasing in U_t.
If a justified capability-to-availability bridge makes U_t(K) nondecreasing
in retained capability, beta is nonincreasing in K. Without that bridge,
K alone has no implication for the bound.

F(K) and institutional delays can constrain the supplied capacity schedule.
They are not inferred from it or estimated by this result. Rebuilding bills
enter path fixed costs; the company's restoration equality root still
depends on both rebuilding expenditure and output shifted within the horizon.
Neither mechanism establishes permanent irreversibility.

If capacity eventually recovers completely, beta can still be positive
because earlier delay/ramp quarters required AI. Report the endpoint floor
separately from accumulated transition exposure. A positive horizon beta is
not proof of lasting dependence after the horizon.

The bound applies to pooled costs of a common input, not one provider's
revenue or profit. It does not identify who caused the price increase,
an equilibrium markup, monopoly, market definition or welfare loss.

## 6. Separate hypothetical illustration

company_scenarios.json declares two independent workload baskets, NOT the
three illustrative companies and NOT an observed sector composition:

| Workload | Human hours for full replacement | Baseline AI spending floor |
| --- | ---: | ---: |
| Sector 1 basket | 8 | 80 |
| Sector 2 basket | 12 | 60 |

Costs are normalized units. H=20, B=140, lambda_min=5, lambda_max=10.
The main horizon is 20 quarters, with no discounting:

| Supplied capacity schedule | Horizon beta | End-quarter floor | Lower bound on cost increase when theta doubles from 1 to 2 |
| --- | ---: | ---: | ---: |
| 20 hours every quarter | 0 | 0 | 0; inconclusive |
| 5 hours every quarter | 1,800 | 90 | 1,800 |
| 4 quarters at zero, followed by supplied recovery steps to 20 | 1,070 | 0 | 1,070; transition exposure only |

The detailed recovery schedule is explicitly supplied in the JSON file.
No optimal workforce schedule, institutional supply estimate, real API price
or rebuilding-expenditure estimate is produced here.

## 7. Implementation and checks

src/exposure/systemic.py implements the closed-form bound using the standard
library. scripts/check_shared_capacity.py exports:

- shared_capacity_bound.csv: profile, horizon/endpoint floors and correctly
  directed price-change bounds.
- shared_capacity_quarters.csv: hours, component bounds and discount weights.
- shared_capacity_bound.inputs.json: configuration, hashes and assumptions.

The full company research runner includes this separate illustration.
tests/test_systemic.py checks hand calculations, finite feasible share
combinations, a supplied cost envelope, price increases and cuts, zero floors,
capacity ordering, scaling, discounting, transition exposure and invalid inputs.
Examples and finite checks supplement the proof; they do not establish
empirical accuracy or originality.

## 8. Contribution status

This makes the shared-institutional-capacity mechanism quantitative without
adding a workforce optimizer. The bound follows elementary capacity accounting
and affine cost-envelope reasoning. Its economic relevance does not establish
that it is a novel theorem. The closest-work comparison and evidence agenda
remain necessary before making a publication claim.
