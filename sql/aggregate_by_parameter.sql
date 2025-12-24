-- Aggregate Performance by Parameter Value
-- This query helps answer: "How does changing 'alpha' affect stability and max temp?"

SELECT 
    p.param_name,
    p.param_value,
    COUNT(m.run_id) as run_count,
    AVG(m.max_temperature) as avg_max_temp,
    MIN(m.max_temperature) as min_max_temp,
    MAX(m.max_temperature) as max_max_temp,
    AVG(m.stability_ratio) as avg_stability,
    SUM(CASE WHEN m.stability_ratio > 0.5 THEN 1 ELSE 0 END) as unstable_runs
FROM metrics m
JOIN parameters p ON m.run_id = p.run_id
WHERE p.param_name IN ('alpha', 'nx', 'dt') -- Customize as needed
GROUP BY p.param_name, p.param_value
ORDER BY p.param_name, p.param_value;
