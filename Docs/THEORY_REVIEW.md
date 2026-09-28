# Formal model review and claim-to-calculation map

Status: internal derivation checkpoint, not a manuscript or novelty assessment.
The results below are derived from the stated model, not external evidence.
Literature comparison and manuscript writing remain separate research work.

## 1. Domain and the two different questions

Fix comparable output, quality, cost coverage and horizon. Costs are expressed
in one currency or normalized unit. Discounting is already included in the
coefficients. For the incumbent and a finite set of supplied feasible alternatives:

$$
J_I(\theta)=A_I+\theta V_I,\qquad
J_z(\theta;K)=A_z(K)+\theta V_z(K),\qquad \theta>0.
$$

All coefficients are nonnegative. A is unshocked cost; V is spending repriced
by the particular shock. A path's V includes all discounted transition bills,
not just dependency at the horizon's end. Human restoration can finish while
its horizon coefficient is still positive. Under a common AI shock, V pools all explicitly
repriced suppliers. An alternative must meet the same output and quality
requirements. Copying continuation without replacing any output is not a
human-restoration option.

Immediate exposure holds the original path fixed. An outside-option threshold
instead compares supplied feasible paths. Neither measures an equilibrium
provider price, legal monopoly, demand elasticity, or an optimal staffing policy.
K is recoverable capability, not immediately usable output or paid headcount.

## 2. Result A: immediate exposure is a spending-share identity

When the baseline is positive:

$$
x_I(\theta)=\frac{J_I(\theta)-J_I(1)}{J_I(1)}
           =(\theta-1)\frac{V_I}{A_I+V_I}.
$$

Proof: subtract the two affine costs and divide by the same path's baseline.
K has no direct effect unless it changes a coefficient or the supplied path.
The formula covers price cuts as well as increases. At a zero baseline,
relative exposure is undefined, not zero.

This identity is a starting point, not an empirical or novel result.

## 3. Result B: the exact first outside-option threshold

Define the first weakly competitive alternative at theta at least one:

$$
t_z=
\begin{cases}
1,& A_z+V_z\leq A_I+V_I,\\
\dfrac{A_z-A_I}{V_I-V_z},
 & A_z+V_z>A_I+V_I\ \text{and}\ V_z<V_I,\\
+\infty,&\text{otherwise},
\end{cases}
\qquad
\theta^{\mathrm{out}}=\min_{z\in\mathcal Z}t_z.
$$

The minimum over an empty set is infinity.

Proof: competitiveness is equivalent to
Az - AI <= theta(VI - Vz). If the path already competes at one, its first
admissible price is one. Otherwise a positive difference in slopes gives the
displayed root, which is above one. A nonpositive difference cannot make a
baseline-more-expensive path competitive as theta increases.

An equality root and a first threshold are different objects. The former can
be below one, absent or non-unique. A weak tie does not imply actual switching.

### Material interpretation boundary: first competition is not lasting protection

If Vz <= VI, a competitive alternative remains competitive at higher theta.
If Vz > VI, an initially cheap alternative can lose competitiveness.
For example:

$$
J_I=100+80\theta,\qquad J_z=80+90\theta.
$$

The first threshold is one, but the alternative is competitive only on
1 <= theta <= 2. At theta=3 it costs 350 versus 340 for continuation.
Consequently, a threshold alone is not a price ceiling or an unconditional
ordering of supplier discipline. Report residual spending and selected costs.
This matters particularly when a common shock reprices rival-provider bills.

## 4. Result C: sufficient conditions for capacity monotonicity

Let KL < KH. Hold the incumbent coefficients fixed. Assume:

1. Every alternative feasible at KL is feasible at KH.
2. For each such matched path, its cost at KL is no lower than its cost at KH
   at every theta >= 1.

Then theta_out(KL) >= theta_out(KH), including infinite thresholds.

Proof: any price at which a low-capacity alternative competes is also a price
at which its matched high-capacity alternative competes. The low-capacity
competitive-price set is therefore a subset of the high-capacity set. Taking
infima gives the inequality.

Coordinate conditions Az(KL) >= Az(KH) and Vz(KL) >= Vz(KH) are sufficient
for condition 2. They are not necessary. K alone does not establish either
condition; a restoration/availability bridge must be specified.

Adding a feasible alternative cannot raise the first threshold when all
existing costs are unchanged. A K-independent rival with V_R < V_I gives an
upper bound of its own threshold. Once that rival binds, further capacity
loss can leave the threshold unchanged. Proposition 1 in MODEL_CONTRACT.md
is a valid special case.

Counterexample to fixed-cost-only reasoning: for incumbent (AI, VI)=(100,80),
alternative (200,60) crosses at 5; alternative (240,0) crosses at 1.75.
A higher alternative fixed bill can coexist with an earlier crossing if
residual provider dependence improves. The K label cannot determine the sign.

## 5. Result D: the dynamic human-restoration root

Use the company contract's unchanged quarterly costs A, V and H. Let:

$$
Q=\sum_t w_t,\qquad S=\sum_t w_t r_t,\qquad F_d=\sum_t w_t f_t.
$$

S is discounted affected output shifted to humans; Fd is the discounted
rebuilding expenditure actually paid within the comparison horizon.
For V>0 and S>0:

$$
J_H-J_I=S(H-\theta V)+F_d,\qquad
\theta_H=\frac HV+\frac{F_d}{VS}.
$$

Proof: the common A costs cancel, and every human-replaced output unit removes
V of baseline incumbent spending and adds H of incremental human cost.
Solving the equality gives the expression.

The conditional gap above the incremental human unit-cost benchmark H/V is
Fd/(VS). Its nonnegative sign follows from the assumptions, not from data.
It is not observed behavioral hysteresis or permanent irreversibility.
Full restoration need not be completed for S to be positive.

With S=0 there is no human substitution inside the horizon. If Fd>0 the path
never breaks even; if Fd=0 its costs equal continuation, but it is not an
additional human outside option.

If V and H are fixed and the functions are differentiable:

$$
\frac{d\theta_H}{dK}
=\frac{F_d'(K)S(K)-F_d(K)S'(K)}{V S(K)^2}.
$$

Fd' <= 0 and S' >= 0 suffice for a nonincreasing root in K. The planned bill
F(K) is not interchangeable with Fd(K): payment timing and unfinished paths
matter. Similarly, a longer delay raises the root if it reduces S while Fd
is unchanged and positive. Delay alone does not guarantee a strict increase.
When Fd=0, the root remains H/V for any positive S.

The company example changes K through a hypothetical bill rule while holding
delay/ramp fixed. It does not identify a causal capability-to-time relationship.

## 6. Result E: higher spending can raise exposure but lower the root

Hold A, H, Fd and positive S fixed; vary V>0. For a price increase and A>0:

$$
\frac{\partial x_I}{\partial V}
=\frac{(\theta-1)A}{(A+V)^2}>0,\qquad
\frac{\partial\theta_H}{\partial V}
=-\frac{H+F_d/S}{V^2}\leq0.
$$

Proof: differentiate Results A and D. A and V here are quarterly quantities
for the company path; the common discount weights cancel from its direct
relative exposure.

This comparative static changes total baseline cost. It does not identify an
effect of adoption, market concentration or provider spending allocation.
Diversification at a fixed total AI budget is a different experiment.

## 7. Result F: shared shocks and the aggregation boundary

For disjoint, correctly scaled sectors using the same currency, horizon and
cost coverage, with positive baseline costs J_s(1):

$$
\Delta J_{\mathrm{total}}=(\theta-1)\sum_s V_{sp},\qquad
x_{\mathrm{total}}=\sum_s \omega_s x_s,\qquad
\omega_s=\frac{J_s(1)}{\sum_u J_u(1)}.
$$

Proof: sum Result A's dollar changes, then divide by total baseline cost.
Shared shocks transmit exposure across sectors, but arbitrary normalized
sector output units cannot supply the required monetary weights.
The hypothetical company examples are not estimates of those weights.

Adaptive costs separate across sectors only when the joint feasible set is
the product of their individual feasible sets:

$$
\min_{(z_s)\in\prod_s\mathcal Z_s}\sum_s J_{sz_s}
=\sum_s\min_{z_s\in\mathcal Z_s}J_{sz_s}.
$$

Proof: each sector minimizes its own term independently. If shared labor,
training or rival-provider capacity constrains the combinations, the joint
feasible set is smaller and the sum of individual minima is only a lower
bound on attainable joint cost.

Example: two sectors each have continuation 100+80theta and a human path
costing 200. At theta=2, independent minima sum to 400. If institutional
capacity permits human replacement in at most one sector, feasible joint
cost is at least 460. The current company calculator does not solve that
shared-capacity allocation problem or justify economy-wide thresholds.
This is a scope boundary, not a new workforce optimization extension.

The [shared-capacity proposition](SHARED_CAPACITY_BOUND.md) now supplies a
quantitative common-input cost-exposure floor from comparable human effort
and qualified-route spending floors. Its elementary proof and code do not
solve a joint allocation policy or establish originality.

## 8. Claim-to-calculation map

| Claim | Type and conditions | Code/check | Illustrative output |
| --- | --- | --- | --- |
| Direct exposure follows affected spending share | Identity; fixed mix, positive baseline | test_exposure_identity | company_exposure.csv |
| First threshold follows the three-case rule | Affine equal-output comparison | test_threshold_cases | company_paths.csv; company_summary.csv |
| A baseline alternative can lose competitiveness | Counterexample; higher residual slope | test_baseline_competition_is_not_a_price_ceiling | Path costs, not a standalone empirical table |
| Capacity erosion can weakly raise a threshold | Proposition; nested options and cost order | test_capacity_order_and_rival_bound | capacity_sensitivity.csv |
| Larger fixed rebuilding costs alone do not order thresholds | Counterexample when residual dependence changes | test_fixed_cost_alone_does_not_order_thresholds | rival_constraints.csv is a related, separately controlled example |
| Free rebuilding can have the same root despite delay | Dynamic boundary case; positive shifted output | test_free_restoration_delay_limit | reconstitution_cost_sensitivity.csv; timing tests |
| Completed restoration can include earlier incumbent bills | Horizon accounting, not ending dependence | test_completed_restoration_retains_transition_bills | company_quarters.csv; company_paths.csv |
| Higher spending can mean more exposure and an earlier root | Conditional comparative static | test_spending_comparative_statics | spending_sensitivity.csv |
| Shared monetary shocks sum with spending weights | Identity; valid population/scaling | test_shared_shock_weighted_exposure | No observed aggregate supplied |
| Shared capacity can invalidate independent adaptive minima | Conditional aggregation boundary | test_shared_capacity_bounds | No joint-capacity solver or economy-wide estimate supplied |

Tests are in tests/test_theory_relationships.py. They check finite examples and
boundaries; the proofs, not a scenario grid, justify the general statements.
CSV tables are in data/processed/company_model/ and remain hypothetical.
The shared-capacity bound and its separate illustration are checked in
tests/test_systemic.py; they are not inferred from the company examples.

## 9. Review disposition and remaining work

The affine formulas and existing special-case proposition are internally
consistent. The material correction is to avoid treating a first threshold as
lasting protection without checking residual price sensitivity. The nested
feasibility assumptions and paid-within-horizon restoration accounting must
remain explicit.

This establishes a mathematical checkpoint under fixed demand, fixed technology,
supplied paths and exogenous feasible sets. It does not establish academic
originality, endogenous investment/skill erosion, strategic provider pricing,
market definition, welfare or real-world institutional rebuilding magnitudes.
Next research input: a focused closest-work comparison and defensible
institutional cost/time/feasibility bounds collected by the authors.

A targeted [closest-work comparison](LITERATURE_COMPARISON.md) now records
four primary references, their overlap and reading limits. It does not
establish originality. A distinct theoretical contribution still needs to be
located against the closest models; additional hypothetical grids alone
will not resolve that question.
