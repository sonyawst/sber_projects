-- Формирование отчета в требуемом формате
SELECT 
    t.trial_id,
    COUNT(DISTINCT m.patient_id) AS participants,
    COUNT(DISTINCT CASE WHEN p.gender = 'Male' THEN p.patient_id END) AS males,
    COUNT(DISTINCT CASE WHEN p.gender = 'Female' THEN p.patient_id END) AS females,
    ROUND(AVG(p.age), 1) AS avg_age,
    ROUND(AVG(CASE WHEN m.drug = 'Плацебо' THEN m.condition_score END), 1) AS avg_placebo,
    ROUND(AVG(CASE WHEN m.drug != 'Плацебо' THEN m.condition_score END), 1) AS avg_real_drug,
    t.trial_name
FROM 
    trials t
JOIN 
    measurements m ON t.trial_id = m.trial_id
JOIN 
    patients p ON m.patient_id = p.patient_id
GROUP BY 
    t.trial_id, t.trial_name
ORDER BY 
    t.trial_id;