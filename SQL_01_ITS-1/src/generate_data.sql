INSERT INTO patients (name, age, gender, condition)
WITH RECURSIVE gen_patients AS (
    SELECT 1 AS id
    UNION ALL
    SELECT id + 1 FROM gen_patients WHERE id < 25
)
SELECT 
    'Пациент '  id,
    18 + abs(random() % 60), -- возраст от 18 до 78
    CASE abs(random() % 2) WHEN 0 THEN 'Male' ELSE 'Female' END,
    CASE abs(random() % 10)
        WHEN 0 THEN 'Гипертония'
        WHEN 1 THEN 'Диабет'
        WHEN 2 THEN 'Астма'
        WHEN 3 THEN 'Артрит'
        WHEN 4 THEN 'Депрессия'
        WHEN 5 THEN 'Мигрень'
        WHEN 6 THEN 'Остеопороз'
        WHEN 7 THEN 'Аллергия'
        WHEN 8 THEN 'Гастрит'
        ELSE 'Бессонница'
    END
FROM gen_patients;

INSERT INTO trials (trial_id, trial_name, start_date, end_date)
VALUES
    (1, 'Исследование эффективности Атропина', '2023-01-15', '2023-06-15'),
    (2, 'Клинические испытания Бисопролола', '2023-02-01', '2023-07-01'),
    (3, 'Изучение воздействия Ибупрофена', '2023-03-10', '2023-08-10'),
    (4, 'Тестирование Аторвастатина', '2023-04-05', '2023-09-05'),
    (5, 'Оценка эффективности Добутамина', '2023-05-20', '2023-10-20'),
    (6, 'Исследование Ацетилцистеина', '2023-06-15', '2023-11-15');

INSERT INTO measurements (patient_id, trial_id, measurement_date, drug, condition_score)
WITH RECURSIVE 
nums(id) AS (
    SELECT 1 UNION ALL SELECT id + 1 FROM nums WHERE id < 250
),
trial_data AS (
    SELECT 
        t.trial_id,
        t.start_date,
        t.end_date,
        julianday(t.end_date) - julianday(t.start_date) as duration_days,
        CASE t.trial_id
            WHEN 1 THEN 'Атропин'
            WHEN 2 THEN 'Бисопролол'
            WHEN 3 THEN 'Ибупрофен'
            WHEN 4 THEN 'Аторвастатин'
            WHEN 5 THEN 'Добутамин'
            WHEN 6 THEN 'Ацетилцистеин'
        END as real_drug,
        random() as rnd  -- Для случайной сортировки
    FROM trials t
),
expanded_data AS (
    SELECT 
        (abs(random() % 25) + 1) as patient_id,
        trial_id,
        start_date,
        duration_days,
        real_drug,
        rnd
    FROM trial_data
    CROSS JOIN (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 
                UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10
                UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15
                UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION SELECT 20 
                UNION SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION SELECT 25
                UNION SELECT 26 UNION SELECT 27 UNION SELECT 28 UNION SELECT 29 UNION SELECT 30
                UNION SELECT 31 UNION SELECT 32 UNION SELECT 33 UNION SELECT 34 UNION SELECT 35
                UNION SELECT 36 UNION SELECT 37 UNION SELECT 38 UNION SELECT 39 UNION SELECT 40
                UNION SELECT 41 UNION SELECT 42) as multiplier
    ORDER BY rnd
    LIMIT 250
)
SELECT 
    patient_id,
    trial_id,
    date(start_date, '+' || (abs(random() % duration_days)) || ' days') as measurement_date,
    CASE abs(random() % 3) WHEN 0 THEN 'Плацебо' ELSE real_drug END as drug,
    abs(random() % 101) as condition_score
FROM expanded_data;