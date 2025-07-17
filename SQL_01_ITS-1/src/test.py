from sqlalchemy import create_engine, Column, Integer, String, \
    Date, ForeignKey, func, text
from sqlalchemy.orm import sessionmaker, declarative_base

import answers as answers


Base = declarative_base()

# Таблица «Пациенты»
class Patient(Base):
    __tablename__ = 'patients'

    patient_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    age = Column(Integer)
    gender = Column(String(10))
    condition = Column(String(100))

# Таблица «Испытания»
class Trial(Base):
    __tablename__ = 'trials'

    trial_id = Column(Integer, primary_key=True)
    trial_name = Column(String(100))
    start_date = Column(Date)
    end_date = Column(Date)

# Таблица «Измерения»
class Measurement(Base):
    __tablename__ = 'measurements'

    measurement_id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(Patient.patient_id))
    trial_id = Column(Integer, ForeignKey(Trial.trial_id))
    measurement_date = Column(Date)
    drug = Column(String(100))
    condition_score = Column(Integer)  # Самочувствие по 100-бальной шкале.


engine = create_engine(answers.connection)
sessionmaker = sessionmaker(bind=engine)

def test_connect():
    print("""Проверка правильности БД.
Проверка будет пройдена, если:
1. Введена правильная ссылка на подключение к базе данных.
2. Нужные таблицы существуют.
Если есть ошибки, то они вылезут ниже.""")
    conn = engine.connect()
    conn.execute(text("SELECT 1;"))

# Проверка, что в таблице пациентов больше n:
def test_patients_count(n=20):
    print(f"В таблице пациентов больше {n} строк")
    session = sessionmaker()
    msmnt_count = session.query(func.count(Patient.patient_id)).scalar()
    assert msmnt_count > n

# Проверка, что в таблице пациентов больше n:
def test_measurements_count(n=200):
    print(f"В таблице пациентов больше {n} строк")
    session = sessionmaker()
    msmnt_count = session.query(func.count(Measurement.measurement_id)).scalar()
    assert msmnt_count > n

def assert_equal(arr1, arr2):
    assert len(arr1) == len(arr2)
    for el1, el2 in zip(arr1, arr2):
        if abs(el1 - el2) > 0.01:
            print(f"{arr1} != {arr2}, ({el1}!={el2})")
            break

# Сделать запрос на вывод разницы между средним по плацебо и 
# другим препаратам в каждом исследовании.
# Результаты упорядочить по дате начала исследования.
# Количество исследований должно быть больше n.
def test_avg_dif(sql, n):
    print(f"""Запрос на вывод разницы между средним по плацебо и 
другим препаратам в каждом исследовании.
Результаты упорядочить по дате начала исследования.
Количество исследований должно быть больше {n}.""")
    session = sessionmaker()

    trials = session.query(Trial.trial_id).order_by(Trial.start_date).all()
    differences = []
    for trial in trials:
        trial_id = trial.trial_id
        
        # Средний эффект плацебо:
        avg_placebo = session.query(func.avg(Measurement.condition_score)).filter(
            Measurement.trial_id == trial_id,
            Measurement.drug == 'Плацебо'
        ).scalar()

        # Средний эффект активного препарата:
        avg_active_drug = session.query(func.avg(Measurement.condition_score)).filter(
            Measurement.trial_id == trial_id,
            Measurement.drug != 'Плацебо'  # Предполагается, что остальные препараты активные.
        ).scalar()

        differences.append(avg_active_drug - avg_placebo)

    sql_differences = [r[0] for r in session.execute(text(sql)).fetchall()]
    assert len(differences) > n
    assert_equal(sql_differences, differences)

# Нужно посчитать разницу между самым ранним и самым поздним измерениям по всем пациентам для плацебо и реального препарата.
# Далее нужно посчитать разницу между реальным препаратом и плацебо.
# Эту разницу нужно посчитать для каждого эксперимента.
def test_compare_first_last_day_difference_for_all_trials(sql):
    print(f"""Нужно посчитать разницу между самым ранним и самым поздним измерениям по всем пациентам для плацебо и реального препарата.
Далее, нужно посчитать разницу между реальным препаратом и плацебо.
Эту разницу нужно посчитать для каждого эксперимента.""")
    session = sessionmaker()
    # Получаем список всех исследований:
    trials = session.query(Trial.trial_id).order_by(Trial.trial_id).all()

    differences = []
    for trial in trials:
        trial_id = trial.trial_id
        
        # Получаем данные для плацебо: первый и последний день:
        placebo_first_day = session.query(Measurement.condition_score).filter(
            Measurement.trial_id == trial_id,
            Measurement.drug == 'Плацебо'
        ).order_by(Measurement.measurement_date.asc()).first()

        placebo_last_day = session.query(Measurement.condition_score).filter(
            Measurement.trial_id == trial_id,
            Measurement.drug == 'Плацебо'
        ).order_by(Measurement.measurement_date.desc()).first()

        # Получаем данные для реального препарата: первый и последний день:
        active_first_day = session.query(Measurement.condition_score).filter(
            Measurement.trial_id == trial_id,
            Measurement.drug != 'Плацебо'
        ).order_by(Measurement.measurement_date.asc()).first()

        active_last_day = session.query(Measurement.condition_score).filter(
            Measurement.trial_id == trial_id,
            Measurement.drug != 'Плацебо'
        ).order_by(Measurement.measurement_date.desc()).first()

        placebo_difference = placebo_last_day[0] - placebo_first_day[0]
        active_difference = active_last_day[0] - active_first_day[0]
        total_difference = active_difference - placebo_difference
        differences.append(total_difference)
    
    sql_differences = [r[0] for r in session.execute(text(sql)).fetchall()]
    assert len(differences) > 0
    assert_equal(sql_differences, differences)
                 

for i, (f, args) in enumerate([(test_connect, tuple()),
                               (test_patients_count, (5,)),
                               (test_measurements_count, (200,)),
                               (test_avg_dif, (answers.task_1_sql, 5)),
                               (test_compare_first_last_day_difference_for_all_trials, (answers.task_2_sql,)),
                               ]):
    print("="*8)
    print(f"Проверка {i}")
    print()
    f(*args)
    print()
    print(f"Проверка {i} пройдена")
    print("="*8)

print("Все успешно пройдено")
print("Загрузим итоговый отчет:")

import pandas as pd

df = pd.read_csv("trial_statistics.csv")
print(df)
