from exposure.threshold import cheapest_path
from exposure.provider import provider_profit, provider_revenue

sectors = [
    [(100,80), (180,20)],
    [(100,80), (260,0)]
]

for paths in sectors:
    print(cheapest_path(paths, 1.5))

print(provider_revenue(sectors,1.0))
print(provider_revenue(sectors,1.5))
# Hypothetical constant marginal cost; fixed provider costs are omitted.
print(provider_profit(sectors, 1.0, 0.25))
print(provider_profit(sectors, 1.5, 0.25))
