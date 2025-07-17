 CREATE TABLE patients (
    patient_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    condition VARCHAR(100)
);
CREATE TABLE trials (
    trial_id INTEGER PRIMARY KEY,
    trial_name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    CONSTRAINT valid_dates CHECK (end_date IS NULL OR end_date >= start_date)
);
CREATE TABLE measurements (
    measurement_id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    trial_id INTEGER NOT NULL,
    measurement_date DATE NOT NULL,
    drug VARCHAR(100),
    condition_score INTEGER CHECK (condition_score >= 0 AND condition_score <= 100),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (trial_id) REFERENCES trials(trial_id)
);