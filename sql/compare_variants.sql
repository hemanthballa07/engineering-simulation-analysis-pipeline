-- Compare Variants / Find Top Performers
-- This query helps answer: "Which configurations provided the highest temperature without becoming unstable?"

SELECT 
    m.run_id,
    m.max_temperature,
    m.stability_ratio,
    p_alpha.param_value as alpha,
    p_nx.param_value as nx,
    m.energy_like_metric
FROM metrics m
-- pivoting parameters for readability
LEFT JOIN parameters p_alpha ON m.run_id = p_alpha.run_id AND p_alpha.param_name = 'alpha'
LEFT JOIN parameters p_nx ON m.run_id = p_nx.run_id AND p_nx.param_name = 'nx'
WHERE m.stability_ratio <= 0.5 -- Filter for stable runs only
ORDER BY m.max_temperature DESC
LIMIT 10;
