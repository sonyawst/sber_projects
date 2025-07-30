import sqlite3
from config import DB_FILE

def init_db():
    """Создает таблицу в SQLite, если её нет"""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS stroke_risk_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id BIGINT NOT NULL,
            gender TEXT NOT NULL,
            age INTEGER NOT NULL,
            hypertension INTEGER NOT NULL,
            heart_disease INTEGER NOT NULL,
            ever_married INTEGER NOT NULL,
            work_type TEXT NOT NULL,
            residence_type INTEGER NOT NULL,
            avg_glucose_level REAL,
            bmi REAL,
            smoking_status TEXT NOT NULL,
            probability REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        print("✅ Таблица 'stroke_risk_users' готова в SQLite.")
    except Exception as e:
        print(f"❌ Ошибка при создании таблицы: {e}")
    finally:
        if conn:
            conn.close()

def save_user_data(chat_id, user_data, probability):
    """Сохраняет данные пользователя в SQLite"""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO stroke_risk_users (
            chat_id, gender, age, hypertension, heart_disease, ever_married,
            work_type, residence_type, avg_glucose_level, bmi, smoking_status, probability
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        cursor.execute(insert_query, (
            chat_id,
            user_data["gender"],
            user_data["age"],
            user_data["hypertension"],
            user_data["heart_disease"],
            user_data["ever_married"],
            user_data["work_type"],
            user_data["Residence_type"],
            user_data.get("avg_glucose_level"),
            user_data.get("bmi"),
            user_data["smoking_status"],
            probability
        ))
        conn.commit()
        print(f"✅ Данные пользователя {chat_id} сохранены в SQLite.")
    except Exception as e:
        print(f"❌ Ошибка при сохранении данных: {e}")
    finally:
        if conn:
            conn.close()

def get_last_user_data():
    """Получает последнюю запись из БД (для теста)"""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stroke_risk_users ORDER BY created_at DESC LIMIT 1;")
        return cursor.fetchone()
    except Exception as e:
        print(f"❌ Ошибка при получении данных: {e}")
        return None
    finally:
        if conn:
            conn.close()