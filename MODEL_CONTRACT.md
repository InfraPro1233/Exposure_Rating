# Phase 0 Model Contract

Status: **Theory framework ready for review**. Updated: 2026-09-27.

## Current primary application: company data under institutional scarcity

The reusable company-input relationship is the primary practical application.
Keep company spending, incremental replacement labor, retained capability and
immediately available human substitution separate from institution-level
rebuilding expense, timing and feasibility. The controlling input split and
three hypothetical examples are in [COMPANY_INPUT_CONTRACT.md](Docs/COMPANY_INPUT_CONTRACT.md).
Specific model/API prices are not required. SWE-bench remains an optional worked
software example, not the paper's foundation. Outside-option thresholds do not
establish unrestricted pricing or monopoly.

The independent [shared-capacity bound](Docs/SHARED_CAPACITY_BOUND.md)
extends the framework to common AI-input shocks when human substitution
plans compete for institutional productive capacity. It uses comparable
productive hours, not summed unlike task counts, and produces a conditional
cost-exposure floor rather than an allocation optimizer or monopoly estimate.
The [research package](Docs/RESEARCH_PACKAGE.md) is the handoff and manuscript
blueprint; it keeps the final paper separate from this implementation.

## General model: cross-sector dependence and supplier pricing power

The central object is a **theoretical quantitative relationship**: how AI adoption, retained human capacity, provider concentration, and feasible alternatives affect a supplier's potential pricing power. A firm or sector may insert its own data. The SWE-bench observations form the planned software-engineering application. Finance, healthcare, and other sectors require their own task, quality, labor, regulatory, provider-access, and restoration inputs for numerical application.

The paper's core deliverables are definitions, a transparent company/institutional model, propositions or comparative statics, boundary cases, and three illustrative company applications. The software application is optional. Data quality determines what an application can claim; it does not determine whether the theoretical relationships can be derived. A focused comparison with related theory and internal consistency checks are required.

Use sector index \(s\), provider index \(p\), and, where needed, firm index \(f\). Each sector has a comparable within-sector output unit, volume \(N_s\), adoption \(D_s\), retained human capability \(K_s\), task mix \(q_s\), human unit cost \(B_s\), agent unit costs \(E_{si}\), and sector-specific restoration paths \(F_s,\tau_s\). A shared provider can impose a common or provider-specific price multiplier across sectors. At fixed allocations, a minimal cost relationship is

$$
TC_s(\boldsymbol\theta)=N_s\left[D_s\sum_i a_{si}E_{si}(\theta_{p(i)})+(1-D_s)B_s\right].
$$

For the execution-only case \(E_{si}(\theta_p)=\theta_p C_{si}/P_{si}\), the provider's **immediate dollar exposure** is the price change times that provider's initial execution spending. This is an accounting identity, not evidence of market power. Retained capacity \(K_s\) enters through feasible human substitution and restoration, not directly through the fixed-mix exposure formula. Do not combine normalized task counts across unlike sectors. Sum dollar costs/exposure only when actual sector volumes, comparable cost coverage, and non-overlapping populations are justified.

### Minimal formal comparison

For a firm or sector, hold output and quality fixed over horizon \(T\). Express the incumbent continuation path and each feasible outside-option path \(z\) as

$$
J_I(\theta_p)=A_I+\theta_p V_I,\qquad
J_z(\theta_p;K)=A_z(K)+\theta_p V_z(K).
$$

Here \(A\) includes all costs not shocked by provider \(p\), including non-duplicated switching/restoration outlays and delay costs; \(V\) is that provider's direct execution spending over the horizon. A path is eligible only if it meets the same output and quality constraints and is physically feasible. Define

$$
\theta^{\mathrm{out}}_p(K)=\inf\{\theta_p\geq1:\min_{z\in\mathcal Z(K)}J_z(\theta_p;K)\leq J_I(\theta_p)\}.
$$

If one path has \(V_z<V_I\) and no cheaper alternative at baseline, its crossing is \((A_z-A_I)/(V_I-V_z)\), restricted to \(\theta_p\geq1\); the first feasible crossing across paths determines the threshold. Define the threshold as \(+\infty\) when no feasible alternative crosses at or above baseline, and report a baseline-competitive alternative as threshold \(1\). The path's residual provider dependence \(V_z\) matters: rebuilding people while still buying the incumbent's tools may offer little protection. Lower \(K\) raises the threshold only under explicit assumptions that it weakly increases alternative fixed costs and/or removes feasible alternatives without improving their provider dependence. Do **not** assert an unconditional sign. Likewise, a larger incumbent provider share increases immediate exposure but can make a viable low-dependence outside option attractive **sooner**; concentration by itself need not increase the threshold. These conditional or opposing comparative statics are the central mathematical problem.

### Threshold interpretation boundaries

A first weakly competitive alternative need not remain competitive at higher
prices. Lasting cost protection follows for a given alternative when its
residual shocked spending is no greater than the incumbent's. If its spending
slope is higher, a baseline-cheap option can lose competitiveness as prices
rise. For example, an alternative costing 80+90theta competes with an
incumbent costing 100+80theta at theta=1, but becomes more expensive above
theta=2. Its first threshold is 1, not a lasting price ceiling.

Residual spending in the quarterly model is accumulated discounted spending
over the comparison horizon. It includes transition bills during restoration;
a positive coefficient does not necessarily imply dependency at the horizon's
end. Report ending output and capability separately.

Shared institutional constraints also matter. Summing each sector's cheapest
feasible path gives an attainable joint cost only when those paths can be
supplied together. Otherwise it is an optimistic lower bound, not an estimate
of economy-wide restoration cost.

The detailed derivations, sufficient capacity-ordering conditions, dynamic
root, cross-sector aggregation boundary and claim-to-calculation map are in
[THEORY_REVIEW.md](Docs/THEORY_REVIEW.md). They establish internal mathematical
conditions, not originality relative to the literature.

### Proposition 1: human-capacity erosion with a feasible rival

Fix one user or sector, output and quality, and horizon \(T\). Suppose \(V_I>0\); the incumbent path \(J_I=A_I+\theta_pV_I\) does not vary with \(K\); immediate human restoration is feasible for every \(K\) under comparison and costs \(J_H(K)=B_T+F(K)\), with no remaining spending on provider \(p\); and a rival path \(J_R=A_R+\theta_pV_R\) is feasible, independent of \(K\), and has \(0\leq V_R<V_I\). Let \(F(K)\) be nonincreasing in retained capacity. Then

$$
\theta_H(K)=\max\left\{1,\frac{B_T+F(K)-A_I}{V_I}\right\},
\qquad
\theta_R=\max\left\{1,\frac{A_R-A_I}{V_I-V_R}\right\},
\qquad
\theta_p^{\mathrm{out}}(K)=\min\{\theta_H(K),\theta_R\}.
$$

**Proof.** Subtract \(J_I\) from each alternative's cost and solve each linear inequality \(J_z\leq J_I\) over \(\theta_p\geq1\). The first crossing across the two feasible paths is their minimum. Because \(F(K)\) is nonincreasing, \(\theta_H(K)\) and hence its minimum with constant \(\theta_R\) are nonincreasing in \(K\). Thus lowering \(K\) can weakly raise the outside-option threshold, but cannot push it above the rival threshold. Where human restoration uniquely sets a threshold above one and \(F\) is differentiable, \(d\theta_p^{\mathrm{out}}/dK=F'(K)/V_I\leq0\); where the rival sets it, the derivative is zero. This proposition concerns a cost threshold, not the provider's chosen price or profit.

**Counterexample to a strict lock-in claim.** In the hypothetical one-period example \(A_I=100\), \(V_I=80\), \(B_T=200\), \(F(K)=200(1-K)\), \(A_R=180\), and \(V_R=20\). Then \(\theta_H(K)=3.75-2.5K\) and \(\theta_R=4/3\). For every \(K\leq29/30\), the rival binds, so further human-capacity erosion leaves the overall threshold unchanged. The plotted capacity grid illustrates this proposition; it does not establish that either path is feasible in a real sector. If the human path is infeasible, only the rival threshold remains; if neither path is feasible, this model reports \(+\infty\).

Define the supplier's **outside-option threshold** for a specified horizon as the lowest provider-price multiplier, if any, at which a stated feasible alternative path (qualified rival provider, human restoration, or a combination) costs no more than continuing with the incumbent. Compare paths at equal output, quality, horizon, and cost coverage, including switching and restoration costs and delay. A higher threshold indicates weaker modeled substitution discipline under those assumptions; it is **not** an estimated optimal markup or proof of monopoly. Report no crossing and infeasible alternatives explicitly. Multiple customers' thresholds may differ; do not label one firm's threshold an economy-wide price ceiling.

The paper tests **potential supplier pricing power**, not whether any named provider currently has a legal monopoly. Actual market power or monopoly claims require separate evidence on market definition, elasticities, entry, contracts, rival capacity and quality, strategic pricing, and observed conduct. Cross-sector interdependence matters because a shared compute supplier can affect many sectors simultaneously, while sector-specific human capacity and regulatory barriers can make their outside options unequal. Economy-wide numerical exposure remains unavailable without representative sector coverage and weights.

This document defines the research scope, quantities, accounting conventions, comparison baselines, scenario settings, and unresolved calibration questions. The parameter dictionary and open-assumptions register are included here rather than split across additional files. The current manuscript blueprint and remaining evidence requirements are in [RESEARCH_PACKAGE.md](Docs/RESEARCH_PACKAGE.md); software-specific sections below describe the optional application.

The user owns implementation and research calculations. This contract supplies their specification; it does not implement a simulation or claim empirical calibration. Numerical values requiring evidence remain unfilled. The normalization, scenario grids, and explicitly hypothetical examples below are design choices.

## 1. Research scope and questions

The intended paper develops a general mathematical model of dependence on AI suppliers. It investigates how agent adoption \(D_s\), retained human capacity \(K_s\), provider allocation, and the cost and feasibility of outside options affect exposure to a provider-specific price increase. The model applies at firm and sector levels; a cross-sector calculation requires sector-specific task units and defensible weights.

| Research question | Required theoretical result |
| --- | --- |
| How does a provider price change affect a fixed production mix? | Spending-share exposure identity and its domain of validity |
| When can users switch? | Existence and value of an outside-option threshold over a common horizon |
| When does lower human capacity increase pricing headroom? | Conditions on restoration costs, delay, feasibility, and residual provider dependence; counterexamples |
| What does provider concentration imply? | Separate results for immediate exposure and switching threshold; no unconditional monopoly inference |
| How does the relationship extend across sectors? | Sector-specific thresholds and shared-shock relationships, with aggregation limits |
| How is the model used? | SWE-bench software application and optional hypothetical firm parameterizations |

### 1.1 Contribution and limits

The contribution must come from a clearly stated relationship, proof or qualified comparative static, and an informative counterexample or boundary case. Immediate exposure equals the price change times affected execution spending under fixed allocation; that identity is a starting point. A positive static restoration bill also widens a simple reversal-cost gap by construction. Neither identity alone establishes novelty or supplier market power.

The outside-option threshold is a conditional measure of substitution discipline. It does not identify an observed markup, legal monopoly, equilibrium provider price, or social welfare loss. The model assumes stated output, quality, cost paths, and a feasible-option set. If a path becomes infeasible or prices alter demand, its threshold must be re-evaluated under those changed assumptions.

### 1.2 Theory checkpoint and software application

Before broad simulation, specify the feasible paths; derive the immediate-exposure identity and threshold crossing cases; identify conditions for monotonicity in \(K\) and provider availability; test counterexamples, zero-switching-cost limits, and no-crossing cases; and compare with closely related switching-cost, lock-in, and market-power theory. A large scenario grid cannot replace this work.

The SWE-bench Verified Bash Only / mini-SWE-agent observations supply agent cost and resolution inputs for a worked software example. Human task cost, adoption, capacity, and restoration values may remain transparent scenario inputs. The example reports what follows under those values; empirical claims require matched data and an explicit benchmark-to-production bridge. Hypothetical firms may demonstrate how organizations replace the scenario inputs with their own, but they do not determine economy-wide weights.

Use **reversal-cost gap** as a neutral threshold difference and **automation lock-in wedge** only as defined shorthand. Neither term proves permanent irreversibility or that AI caused human-capacity loss.

The remaining sections give the **software application contract**. They use one eligible task basket and suppress the sector index. A finance or healthcare application must supply its own comparable output unit, cost inputs, feasibility rules, and restoration paths; it cannot import the SWE-bench values.

## 2. Software application: task unit, denominators, and evidence boundary

### 2.1 What one unit means

In the software application, the calibration unit is **one resolved repository issue within the stated benchmark task basket**. The economic output unit is **one comparable completed task-output unit in that basket**. Other sectors must define their own output units. Equating the benchmark proxy with useful production output is an explicit modeling assumption, not an observed fact. Production-acceptance sensitivities will examine that assumption.

Tasks are normalized units, not necessarily identical jobs. The model assumes that the specified basket and its difficulty/quality composition remain comparable across the human and agent portions. It must not compare agents resolving easy issues with humans completing an unadjusted, more difficult residual workload.

Begin with one agent configuration at a time. Explicit model allocations can then form portfolios. A configuration identifies the exact model and agent setup under particular evaluation conditions, not merely a provider or model family.

### 2.2 Cost-to-success accounting

For a matched evaluation, let \(n_i\) be the number of evaluated tasks, \(r_i\) the number resolved, and \(Z_i\) total recorded execution spending:

$$
C_i=\frac{Z_i}{n_i},\qquad P_i=\frac{r_i}{n_i},\qquad
E_i=\frac{C_i}{P_i}=\frac{Z_i}{r_i}\quad\text{when }r_i>0.
$$

The ratio allocates spending on successful and unsuccessful evaluations across resolved output. It does not prove that retrying every failed task independently will eventually succeed at that average cost. Scaling it to maintained production requires an assumption about the applicability of the average and the treatment of unresolved work; that limitation remains visible in all results.

Cost and resolution must cover the same sample and configuration. Check whether spending includes failures, retries, tools, and other execution charges. Missing cost is not zero. A zero resolution rate makes the configuration unavailable for finite-cost comparison. If a source reports dollars per resolved task already, do not divide it by \(P_i\) again.

### 2.3 Human comparison

Human cost must cover comparable work and completion quality. A wage is not a task cost. Where compatible inputs exist:

$$
B=w_Bh_B+b_{\mathrm{other}},
$$

where \(w_B\) is the specified hourly labor cost, \(h_B\) is productive effort per completed comparable task, and \(b_{\mathrm{other}}\) contains only additional, non-overlapping task costs. If effort is unavailable, use a clearly labeled scenario range rather than an empirical point estimate. This still permits a worked application, provided it is not described as a measured AI-versus-human cost comparison.

### 2.4 Provenance labels

- **Observed:** directly extracted measurements, with their actual coverage and definitions.
- **Calibrated:** assumptions or ranges justified using evidence and explicit transformations.
- **Simulated:** imposed experimental conditions and calculated outcomes.
- **Hypothetical:** teaching examples and illustrative firm inputs.

Derived costs must retain links to their inputs. A calculation using observed prices is not automatically an observed industry result.

## 3. Parameter dictionary

Indices: \(i\) identifies a configuration, \(p\) a provider, \(j\) a task category when available, \(t\) a quarter, \(z\) a production path, and \(f\) a hypothetical firm. Subscripts are omitted when a parameter is constant across the stated comparison.

### 3.1 Technology and labor costs

| Parameter | Definition | Unit and admissible values | Input status or rule |
| --- | --- | --- | --- |
| \(n_i,r_i,Z_i\) | Evaluated count, resolved count, and total execution spending | Counts: \(n_i>0\), \(0\leq r_i\leq n_i\); dollars: \(Z_i\geq0\) | Observed where reported; do not fabricate totals from rounded rates |
| \(C_i\) | Mean execution spending per evaluated task, including failures | USD/evaluated task, finite and nonnegative | Matched observation or documented reconstruction |
| \(P_i\) | Benchmark resolved fraction from the same evaluation | Dimensionless, \([0,1]\) | Observed; \(P_i>0\) required for finite effective cost |
| \(\widetilde P_i\) | Alternative production-acceptance assumption | Dimensionless, \([0,1]\) | Calibrated or hypothetical sensitivity, never silently substituted for observed \(P_i\) |
| \(E_i\) | Effective agent cost under the selected accounting regime | USD/completed proxy task | Derived; baseline \(C_i/P_i\) |
| \(H_i\) | Human review effort per evaluated task | Hours/evaluated task, nonnegative | Calibrated or hypothetical extension |
| \(W\) | Review labor cost | USD/hour, positive for paid labor | Observed/calibrated; employer-cost coverage recorded |
| \(R_i\) | Expected rework cost not included in other components | USD/evaluated task, nonnegative | Calibrated or hypothetical extension |
| \(w_B\) | Human production labor cost | USD/productive hour, positive | Calibrated from documented compensation and hours |
| \(h_B\) | Human productive effort for comparable completed work | Hours/completed task, positive | Evidence-based estimate or explicit hypothetical range |
| \(b_{\mathrm{other}}\) | Additional human task costs | USD/completed task, nonnegative | Include only separately justified costs |
| \(B\) | Human cost per comparable completed task | USD/completed task, positive | Derived/calibrated; not identified by wages alone |

### 3.2 Production and pricing

| Parameter | Definition | Unit and admissible values | Input status or rule |
| --- | --- | --- | --- |
| \(N_t\) | Required compatible output in quarter \(t\) | Task-output units/quarter, positive | Main normalization: 1,000; not national task volume |
| \(Q\) | Total required output over the horizon | Task-output units, \(\sum_tN_t\) | Derived from the same horizon used for costs |
| \(D_0,D_t\) | Initial and quarterly agent shares of completed output | Dimensionless, \([0,1]\) | Initial grid; path-derived after restoration begins |
| \(\theta,\theta_p\) | Common or provider-specific multiplier on direct execution prices | Dimensionless, strictly positive | Simulated; baseline is 1 |
| \(a_i\) | Configuration share of agent-mediated output | Dimensionless, nonnegative, \(\sum_i a_i=1\) | Explicit allocation; scenario unless measured |
| \(p(i)\) | Provider supplying configuration \(i\) | Provider identifier | Documented mapping |
| \(s_p\) | Provider share of agent-mediated output | Dimensionless, \(\sum_{i:p(i)=p}a_i\) | Derived; not a spending share |
| \(q_j,a_{ij}\) | Task shares and configuration shares within task category | Nonnegative; \(\sum_jq_j=1\), \(\sum_i a_{ij}=1\) | Later extension requiring matching category costs/outcomes |
| \(\bar E\) | Allocated mean agent cost | USD/completed proxy task | Derived from the same allocation used for the baseline |

### 3.3 Capability, time, and restoration

| Parameter | Definition | Unit and admissible values | Input status or rule |
| --- | --- | --- | --- |
| \(K_0,K_t\) | Initial and subsequent recoverable human capability relative to baseline | Dimensionless, \([0,1]\) | Scenario state; skills and knowledge, not headcount |
| \(A_t\) | Maximum human share of required output available during a quarter under stated staffing/productivity assumptions | Dimensionless, \([0,1]\) | Calibrated or hypothetical path; separate from \(K_t\) |
| \(\widehat h_t,h_t\) | Intended and actual human production shares | Dimensionless, \([0,1]\) | Supplied strategy and constrained result; no optimization |
| \(f_t^{(z)}\) | Incremental restoration expenditure on path \(z\) | USD/quarter, nonnegative | Supplied profile at the chosen production scale |
| \(M_t^{(z)}\) | Paid retention, idle capacity, or other carrying costs not in unit production costs | USD/quarter, nonnegative | Explicit profile; zero is an omission assumption unless justified |
| \(F_T\) | Restoration expenditure incurred through quarter \(T\) | USD, \(\sum_{t=1}^T f_t\) | Derived; report later planned costs separately |
| \(F(K)\) | Shorthand for restoration expenditure conditional on initial capability and other stated assumptions | USD | Not a uniquely identified function of \(K\) alone |
| \(\tau\) | Time to reach both the specified capability and output-capacity targets | Quarters; 0 if initially met | Derived from path; report beyond horizon when appropriate |
| \(\ell,m\) | Delay and ramp duration for a supplied restoration profile | Quarters: \(\ell\geq0\), \(m>0\) | Calibrated/hypothetical; immediate restoration is a separate limit case |
| \(\Delta\ell,\gamma\) | Additional pipeline delay and ramp-duration multiplier | Quarters: \(\Delta\ell\geq0\); multiplier: \(\gamma\geq1\) | Education sensitivity, not inferred directly from enrollment percentages |
| \(T\) | Comparison horizon | Integer quarters: 20 main; 12 and 40 sensitivity | Design choice |
| \(r\) | Annual effective discount rate | Dimensionless, \(r\geq0\) | Main comparison uses 0; positive sensitivities must be stated |

Result quantities are defined below: \(TC\) is period cost, \(X\) dollar exposure, \(x\) fractional exposure, \(J_z\) horizon cost, \(\theta^*\) the adoption cost benchmark, \(\theta^{**}\) a reversal threshold, and \(L\) their difference. Thresholds are price multipliers, not percentages or dollars.

## 4. Monetary and temporal conventions

1. Main normalized output is \(N_t=1{,}000\) units in each quarter. Demand and the eligible task basket remain fixed in the core experiments.
2. A static cost represents one quarter at that normalization. Cumulative comparisons use the same quarters and total output on every path.
3. A price shock begins at the start of the first modeled quarter and remains constant in the core experiment. Endogenous price responses and demand changes are outside the baseline.
4. Raw source costs retain their currency and measurement date. Comparisons use USD on a declared common price basis; the final base year and conversions remain calibration decisions. Unharmonized evidence cannot be silently pooled.
5. Historical execution cost and success remain paired. Repricing a run using current API prices requires documented usage and pricing components; keep both versions separate.
6. Main cumulative costs are undiscounted. Discounted sensitivities use the same annual rate and quarterly end-of-period convention for all paths. Material upfront timing can be modeled separately later; it must not differ silently across comparisons.
7. Use no terminal salvage credit in the main finite-horizon comparison. Report ending capability, availability, and uncompleted restoration because those residual differences limit interpretation.
8. Restore-cost profiles must state their volume basis. Scaling \(N\) alone does not justify scaling real recruiting or training expenditure. Any proportional scaling of restoration costs must be an explicit assumption.

## 5. Technology-cost regimes and baseline production

### 5.1 Initial execution-only calculation

For a single configuration:

$$
E_i(\theta)=\theta\frac{C_i}{P_i},\qquad
TC(D,\theta)=N\left[D E_i(\theta)+(1-D)B\right].
$$

Only direct execution prices change. Task mix, quality/acceptance assumptions, usage intensity, and human unit cost remain fixed. This isolates price exposure rather than combining price and capability improvements.

### 5.2 Explicit model and provider allocation

For a declared portfolio:

$$
E_i(\boldsymbol\theta)=\frac{\theta_{p(i)}C_i}{P_i},\qquad
\bar E(\boldsymbol\theta)=\sum_i a_i E_i(\boldsymbol\theta),
$$

$$
TC(D,\boldsymbol\theta)=N\left[D\bar E(\boldsymbol\theta)+(1-D)B\right].
$$

Hold allocation fixed in the initial shock comparison. Weights represent allocated completed output. A source reporting attempted-work shares cannot be substituted without reconciling the different denominator.

### 5.3 Review, rework, and acceptance sensitivity

$$
E_i(\theta)=\frac{\theta C_i+WH_i+R_i}{P_i}.
$$

All numerator components in this expression use a per-evaluated-task denominator. A per-accepted-task review observation must be converted or entered through a compatible alternative formulation. Count correction labor and fallback exactly once.

If replacing \(P_i\) with \(\widetilde P_i\), retain the benchmark rate separately and disclose that costs/effort are held fixed unless the sensitivity explicitly changes them. An external acceptance gap is not a universal adjustment across models and tasks.

The execution-only baseline is a restricted cost measure, not a claim that review and rework are unnecessary. Its availability does not establish the physical feasibility of unreviewed agent production.

### 5.4 Task categories and switching

Category costs require matching category-level evidence or explicitly hypothetical assumptions:

$$
TC=N\left[D\sum_jq_j\sum_i a_{ij}E_{ij}+(1-D)\sum_jq_jB_j\right].
$$

Do not infer every \(E_{ij}\) from one aggregate leaderboard row. The common \(D\) across task categories is a simplifying assumption, not a measured allocation.

Switching selects the lowest effective cost among explicitly feasible configurations and is an idealized, frictionless bound. Compare each allocation regime against its own unshocked baseline. A common positive price multiplier cannot change rankings in the execution-only \(C_i/P_i\) baseline. Provider diversification does not automatically protect against a system-wide shock.

## 6. Comparison baselines

| Comparison | What changes | What stays comparable | Interpretation |
| --- | --- | --- | --- |
| Immediate price exposure | Execution-price multiplier | Output, basket, allocation, \(D\), human costs, acceptance/effort assumptions | Effect of repricing the existing production structure |
| All-human cost benchmark | Production method | Output, basket, completion quality, time basis | Relative production cost, assuming sufficient human availability |
| Restoration versus continuation | Supplied output shares, availability, restoration and carrying costs | Shock, output, unit-cost regime, horizon, discount convention | Economics of a particular transition path |
| Dynamic price exposure | Price on the same specified path | Path and non-price assumptions | Repricing effect over the horizon, not a transition effect |
| Switching comparison | Feasible allocation rule | Output, quality, price scenario and comparison horizon | Savings from the alternative allocation under its stated assumptions |

### 6.1 Immediate price exposure

$$
X(D,\theta)=TC(D,\theta)-TC(D,1),\qquad
x(D,\theta)=\frac{X(D,\theta)}{TC(D,1)}.
$$

Report \(x\) as a fraction internally and \(100x\) as a percentage. Relative exposure is undefined if baseline cost is zero; do not replace it with zero.

For fixed allocation in the execution-only baseline, writing \(e=\sum_i a_iC_i/P_i\):

$$
X=ND(\theta-1)e,\qquad
x=\frac{D(\theta-1)e}{De+(1-D)B}.
$$

Immediate exposure has no direct \(K\) dependence. High agent output share is not identical to high execution spending share. A \(D\)-by-\(K\) figure must use a genuinely capacity-dependent outcome, such as a cumulative transition-cost comparison.

### 6.2 All-human benchmark

$$
TC_{\mathrm{human}}=NB.
$$

This is a cost benchmark, not an assertion that all-human output is immediately feasible. An increase relative to the original mix can coexist with costs below this benchmark.

## 7. Dynamic capability and restoration contract

### 7.1 Separate capability, availability, and actual output

\(K_t\) describes retained or recoverable skills and knowledge. \(A_t\) describes the human output share available under stated staffing, productivity, and review assumptions. Neither is inferred mechanically from employment or from \(D_t\).

For a supplied path:

$$
h_t=\min\{\widehat h_t,A_t\},\qquad D_t=1-h_t.
$$

No optimization of \(\widehat h_t\) is performed. Initial availability must support the specified initial human output \(1-D_0\); flag contradictory initial states rather than silently changing \(D_0\). Within-quarter availability must be defined consistently with the task output credited for that quarter. Do not credit an end-of-quarter hire with a full quarter's production.

Continuation maintains the original mix only if its availability assumptions support it. Restoration follows a specified movement toward human production. The main target is baseline capability and capacity, \(K_{\mathrm{target}}=A_{\mathrm{target}}=1\). It does not follow that those targets can be reached during every horizon.

The overview's linear ramp is a transparent candidate path, not an empirical law. Its timing convention, initial availability, and capability-to-delay relationship must be specified with the calibration profile before dynamic implementation. A profile may assume no net erosion during rebuilding, but that assumption must be recorded. Other erosion/ramp paths are sensitivity cases rather than inferred behavior.

### 7.2 Review and maintained-output feasibility

Agent production supplies output humans cannot yet cover only while the scenario permits sufficient agent access and oversight. Under the per-evaluation review convention, required review hours are:

$$
N_tD_t\sum_i a_i\frac{H_i}{P_i}.
$$

These hours must fit the review allocation without counting the same hours as direct human production. Availability must reflect the staffing split. An execution-only result can be calculated with unverified oversight assumptions, but it cannot then be labeled physically validated.

Hiring an engineer away from another already-covered US engineering role redistributes capacity; it does not itself add national capability or aggregate availability. Activating idle skills may increase availability without creating new capability. Industry reconstruction therefore requires a separately justified account of available labor, training, re-entry, other entry routes, and productivity development.

For each restoration profile, record the capacity source, covered population, cost and timing evidence, assumed productivity development, volume basis, and whether it adds aggregate availability or merely reallocates it. Firm recruiting/onboarding observations can inform particular costs, but cannot alone identify the industry supply response. Test alternative bridges from \(K\) to \(A_t\), including weak or no dependence where feasible; assigning every low-\(K\) case a slower ramp is an assumption, not evidence of capability erosion causing lock-in.

### 7.3 Expenditure and cumulative comparison

For a supplied path \(z\):

$$
J_z(\theta)=\sum_{t=1}^{T}\left\{
N_t[D_t^{(z)}\bar E(\theta)+(1-D_t^{(z)})B]
+f_t^{(z)}+M_t^{(z)}\right\}.
$$

Restoration expenditure includes incremental costs not already represented in unit costs. Paid idle/retained capacity can enter \(M_t\) separately. Ordinary production wages, human review, and human correction must not appear in multiple components. Continued agent expenditure already captures part of the financial consequence of delayed human output.

Define the transition-cost difference as \(\Delta J=J_{\mathrm{restore}}-J_{\mathrm{continue}}\). Negative values mean the specified restoration path is cheaper over that horizon; positive values mean it is more costly. This is not the same as price exposure on either path, \(J_z(\theta)-J_z(1)\).

For discount sensitivity, multiply each quarter's full cost by \((1+r)^{-t/4}\). Keep the horizon, output, cost coverage, timing, and discounting comparable. Record terminal states with every summary.

## 8. Adoption benchmark and reversal thresholds

For a fixed portfolio and fixed acceptance/effort assumptions, write:

$$
\bar E(\theta)=\theta e+v,\qquad
e=\sum_i a_i\frac{C_i}{P_i},\qquad
v=\sum_i a_i\frac{WH_i+R_i}{P_i}.
$$

The execution-only baseline has \(v=0\). When \(e>0\), the immediate unit-cost break-even benchmark is:

$$
\theta^*=\frac{B-v}{e}.
$$

This benchmark does not incorporate adoption investment or solve a behavioral adoption decision. In fixed mixtures with positive \(D\), the same unit-cost equality gives equality against all-human production when other costs are absent. At \(D=0\), the mix does not identify an adoption crossing.

For full, immediate restoration over identical output \(Q\), a one-time restoration cost \(F\), and no other cost differences, the special case is:

$$
\theta^{**}=\theta^*+\frac{F}{Qe},\qquad L=\theta^{**}-\theta^*.
$$

In the dynamic model, define \(\theta^{**}\) by \(J_{\mathrm{restore}}(\theta^{**})=J_{\mathrm{continue}}(\theta^{**})\). For price-independent paths and the same fixed unit costs, let:

$$
S=\sum_tN_t(D_t^{\mathrm{continue}}-D_t^{\mathrm{restore}}),
$$

$$
\Delta G=\sum_t\left[(f_t^{\mathrm{restore}}+M_t^{\mathrm{restore}})
-(f_t^{\mathrm{continue}}+M_t^{\mathrm{continue}})\right].
$$

When \(S>0\) and \(e>0\):

$$
J_{\mathrm{restore}}-J_{\mathrm{continue}}=S(B-v-\theta e)+\Delta G,
\qquad \theta^{**}=\theta^*+\frac{\Delta G}{Se}.
$$

This closed form is not valid without its fixed-cost/path assumptions. More general switching or time-varying regimes require the actual cumulative cost comparison. If \(S=0\), the stated formula is undefined; equal costs everywhere do not identify a unique root. If costs have no price sensitivity, do not divide by zero.

Keep separate statuses for: an admissible positive root; a root outside the tested price range; no positive root; non-unique or multiple roots; and restoration not attained within the horizon. A partial-restoration path may have an accounting root even when full restoration is not attained; disclose both facts. Do not force the wedge to be positive or clip unavailable roots to a grid endpoint.

The signs implied by these formulas are analytical properties, not simulation discoveries. In particular, \(F>0\), \(Q>0\), and \(e>0\) imply a positive simplified gap by construction. The research question concerns its defensible magnitude and relevance under feasible alternative paths, including whether any crossing occurs in the tested price and time ranges.

## 9. Software scenario register and firm applications

| Experiment | Contracted settings | Evidence boundary |
| --- | --- | --- |
| Adoption | \(D_0=\{.10,.25,.50,.75,.90\}\) | Scenario states, not current US adoption estimates |
| Capability | \(K_0=\{1,.75,.50,.25,.10\}\) | Recoverable capability scenarios, not employment statistics |
| Execution prices | \(\theta=\{.50,.75,1,1.25,1.50,2,3\}\) | Positive and negative price shocks; not forecasts |
| Restoration | Low, medium, high cost/delay/ramp profiles | Values require evidence or explicit hypothetical labels |
| Horizon | 20 quarters main; 12 and 40 sensitivity | Same comparison basis within each horizon |
| Discounting | Undiscounted main; stated positive-rate sensitivities | No undisclosed rate or timing conventions |
| Providers | Common shock; selected-provider shock; concentrated/diversified shares | Shares are scenario allocations unless observed |
| Oversight/acceptance | Execution-only baseline plus stated acceptance, review, and rework ranges | Omitted costs and feasibility assumptions remain visible |
| Education pipeline | Unchanged, moderately constrained, strongly constrained restoration | Additional delay/slower ramp; no direct mapping from enrollment percentage |

The software adoption/capability/price/restoration grid contains 525 combinations before feasibility exclusions and added sensitivities. Initial and path constraints may invalidate combinations; preserve their status rather than silently dropping them. Static exposure does not require redundant \(K\) calculations.

For education sensitivity, use \(\ell_{\mathrm{pipeline}}=\ell+\Delta\ell\) and/or \(m_{\mathrm{pipeline}}=\gamma m\) on the relevant talent-development component. Applying the same delay to experienced-worker re-entry needs separate justification. The Medium 20% enrollment/admissions headline is a source lead, not an established US projection or a value for \(\Delta\ell\), \(\gamma\), or \(K\). No new enrollment-cohort model is required.

| Hypothetical firm | Annual compatible output \(N_f\) | \(D_f\) | \(K_f\) |
| --- | ---: | ---: | ---: |
| A: AI-augmented enterprise | 100,000 | .30 | .90 |
| B: Automation-heavy company | 250,000 | .75 | .40 |
| C: AI-native producer | 50,000 | .95 | .15 |
| D: High use with retained workforce | Unspecified | .85 | .90 |

Use the same functions and definitions for firms and industry. Compare all firms per 1,000 compatible units; divide supplied annual volumes by four for constant-output quarterly paths. Never invent D's volume or infer paid staffing from its \(K\). Provider portfolios such as \((.80,.10,.10)\) and equal thirds are optional hypothetical settings, not measured industry shares. Task-specific weights need matching costs or hypothetical labels.

## 10. Open-assumptions register

Unresolved empirical values are not filled merely to finish this document. They are explicit inputs to later calibration or sensitivities. None of the following has been established by creating this contract.

| ID | Open assumption or missing input | Consequence | Resolution/fallback and phase |
| --- | --- | --- | --- |
| A01 | Selected configurations, complete cost coverage, and matched evaluation samples | Affects whether \(C/P\) is usable | Collect and reconcile original records; exclude incompatible rows. Phases 2–3 |
| A02 | Benchmark-to-production comparability and failed-task treatment | Limits maintained-output and industry interpretation | Document the bridge, examine acceptance/effort sensitivities, and narrow claims if unsupported. Phases 2–3, 8 |
| A03 | Comparable US human effort and fully specified labor cost | Software \(B\) and numerical thresholds are not empirically identified | Gather effort and compensation for measured claims; otherwise label a scenario range. Application phases 2–3 |
| A04 | Common dollar basis and possible run repricing | May confound price dates with model economics | Preserve raw observations; record a selected monetary basis and transformations. Phase 2 |
| A05 | Baseline task basket and configuration/provider allocations | Determines aggregate industry proxy and exposure | Start with one basket and one configuration; add stated allocations, with empirical or hypothetical status. Phases 0–4, 7 |
| A06 | Initial availability and mapping from \(K\) to restoration | Capability does not yet identify productive capacity | Supply coherent availability, staffing, timing, and capability assumptions; test alternatives. Phases 2, 5 |
| A07 | Restoration cost scale, aggregate capacity source, target, delay, ramp timing, and erosion | Determines transition costs and the reversal gap; firm hiring is not an industry supply response | Identify net availability sources, support at least one profile or bound, and test alternate mappings and scaling. Phases 2, 5 |
| A08 | Human review/rework and reviewer availability | Baseline costs may omit labor and feasibility is not verified | Use compatible published ranges or hypothetical sensitivities; explicitly flag unverified oversight. Phases 2, 5, 8 |
| A09 | Provider access, feasible switching, and switching friction | Cheapest-model result may not be attainable | Define eligible alternatives and report frictionless results as a bound. Phase 7 |
| A10 | US education pipeline and capability inflows | Enrollment cannot directly identify \(K\), \(F\), or \(\tau\) | Verify population and metric; justify delay/ramp sensitivities and alternate entry routes. Phases 2, 8 |
| A11 | Discount-rate ranges and endpoint significance | Finite-horizon conclusions may change | Undiscounted main result; explicit horizon/rate sensitivities and terminal-state disclosure. Phases 6, 8 |
| A12 | Category-level task costs, weights, and quality | Aggregate data cannot support a detailed task matrix | Retain one-basket baseline until matching data or explicit hypothetical assumptions exist. Phase 8 |
| A13 | Academic novelty, informative comparison, and external validity | Valid arithmetic alone does not establish contribution | Complete the Section 1.2 theory checkpoint before broad simulation; distinguish identities, qualified propositions, and scenario findings |

Parameters used in a calculation must carry one declared source or assumption record and units. A record should preserve source title/location, publication and observation dates, retrieval date, exact table/field, raw value, population, transformations, limitations, and provenance category. A scalar default in code must not substitute for resolving or labeling an open item.

## 11. Illustrative explanation and verification criteria

### 11.1 Existing hypothetical arithmetic example

These values reproduce the teaching example in the overview; they are not collected US evidence. For \(C=\$12\), \(P=.60\), \(B=\$80\), \(D=.75\), and \(N=1{,}000\):

$$
E=\frac{12}{.60}=\$20,\qquad
TC(.75,1)=1{,}000[.75(20)+.25(80)]=\$35{,}000.
$$

At \(\theta=1.5\), the agent execution unit cost is \(\$30\), total cost is \(\$42{,}500\), and the increase is \(\$7{,}500\), or about \(21.43\%\) of the original mix. The all-human cost benchmark is \(\$80{,}000\). Thus positive price exposure does not establish that agents have become more costly than humans.

The same immediate result applies at different \(K\) values if its inputs are unchanged. Any difference in restoration outcomes must enter through an explicit capacity/path/cost assumption.

### 11.2 Required checks for later implementation

- Match cost and success denominators; distinguish attempted, resolved, and production-accepted outputs.
- Exclude or flag missing/incompatible observations, invalid probabilities, and zero-success finite-cost calculations.
- Verify normalized task/model/provider shares and explicit allocation identities.
- Verify zero exposure at \(\theta=1\) and no direct AI-price exposure at \(D=0\).
- Verify favorable price shocks, linear dollar exposure in the fixed execution-only case, and the absence of artificial immediate \(K\) dependence.
- Check volume scaling only under compatible cost-scaling assumptions, including restoration costs.
- Verify initial availability, quarterly capacity bounds, review-hour feasibility, and maintained output in scenarios labeled feasible.
- Verify that restoration and carrying costs do not duplicate production/review costs.
- Compare threshold roots directly with the same cost equations, including absent and out-of-range roots.
- Verify horizon conversion, discounting convention, and disclosure of terminal states.
- Reproduce identical normalized industry and firm results for identical inputs.

### 11.3 Phase 0 completion boundary

The general theory definition and software-application accounting are drafted for review. This does not claim that propositions have been proved or numerical paths have been calibrated.

The Phase 0 review should confirm that definitions, units, feasible sets, and comparison baselines support the intended derivations. Develop the general propositions before expanding software simulations. Evidence collection and the existing Python workspace can proceed in parallel. The user retains coding and calculation ownership; this contract does not certify publication readiness.
