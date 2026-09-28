Primary sample: all SWE-bench Verified → Bash Only mini-SWE-agent release 2.0.0 rows reporting both % Resolved and Avg. $.

Retrieved 2026-09-25. Source: the SWE-bench team's leaderboard data at commit f42505b21a0eb31a9cc1204caafcbe0da6c1a259 (linked in each CSV row). This selection yields 13 Verified records. Earlier mini-SWE-agent releases are outside the primary sample.

The CSV keeps the source's unrounded `instance_cost` in `avg_cost_usd`; the public table rounds it to cents. The source's total `cost` divided by `instance_cost` is 500 for these records, matching the 500 evaluated instances. `resolution_rate` is the leaderboard's percentage divided by 100. `submission_folder` locates the record in the source JSON. `leaderboard_date` preserves the source's `date` field; it is not asserted to be the evaluation date.

`model_org` is the source's model organization. It does not establish which company billed or hosted a run, so provider concentration needs separate provider identification before use.
