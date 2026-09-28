from exposure.cost import effective_cost,production_cost,relative_exposure

agent_cost = effective_cost(12,0.60)
baseline = production_cost(1000, 0.75, agent_cost, 80)
shocked = production_cost(1000, 0.75, 1.5 * agent_cost, 80)
exposure = relative_exposure(baseline,shocked)

print("hypothetical example")
print("Baseline:", baseline)
print("Shocked:", shocked)
print("Relative exposure:", exposure)

