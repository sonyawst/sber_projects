connection = "sqlite:///my_database.db"
task_1_sql = """
SELECT 
    AVG(CASE WHEN m.drug = 'Плацебо' THEN m.condition_score ELSE NULL END) - 
    AVG(CASE WHEN m.drug != 'Плацебо' THEN m.condition_score ELSE NULL END) AS difference
FROM 
    trials t
JOIN 
    measurements m ON t.trial_id = m.trial_id
GROUP BY 
    t.trial_id
ORDER BY 
    t.start_date;
"""
task_2_sql = """
WITH placebo_data AS (
    SELECT 
        t.trial_id,
        FIRST_VALUE(m.condition_score) OVER (
            PARTITION BY t.trial_id 
            ORDER BY m.measurement_date
        ) AS first_score,
        LAST_VALUE(m.condition_score) OVER (
            PARTITION BY t.trial_id 
            ORDER BY m.measurement_date
            RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS last_score
    FROM 
        trials t
    JOIN 
        measurements m ON t.trial_id = m.trial_id
    WHERE 
        m.drug = 'Плацебо'
    GROUP BY 
        t.trial_id, m.measurement_date, m.condition_score
),
drug_data AS (
    SELECT 
        t.trial_id,
        FIRST_VALUE(m.condition_score) OVER (
            PARTITION BY t.trial_id 
            ORDER BY m.measurement_date
        ) AS first_score,
        LAST_VALUE(m.condition_score) OVER (
            PARTITION BY t.trial_id 
            ORDER BY m.measurement_date
            RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS last_score
    FROM 
        trials t
    JOIN 
        measurements m ON t.trial_id = m.trial_id
    WHERE 
        m.drug != 'Плацебо'
    GROUP BY 
        t.trial_id, m.measurement_date, m.condition_score
)
SELECT 
    (d.last_score - d.first_score) - (p.last_score - p.first_score) AS difference
FROM 
    drug_data d
JOIN 
    placebo_data p ON d.trial_id = p.trial_id
GROUP BY 
    d.trial_id, d.first_score, d.last_score, p.first_score, p.last_score
ORDER BY 
    (SELECT start_date FROM trials WHERE trial_id = d.trial_id);
"""
