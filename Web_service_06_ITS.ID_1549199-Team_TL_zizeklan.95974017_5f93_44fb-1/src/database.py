# database.py (заглушка)
from typing import Dict, Any

# Вместо реальной БД будем использовать словарь в памяти
fake_db = {}

def init_db():
    """Инициализация 'базы данных' (заглушка)"""
    print("Инициализация базы данных (заглушка)")
    fake_db.clear()

def save_user_data(user_id: int, data: Dict[str, Any], probability: float):
    """Сохранение данных в 'базу' (заглушка)"""
    print("\n=== Сохранение данных (заглушка) ===")
    print(f"User ID: {user_id}")
    print("Данные пользователя:")
    for key, value in data.items():
        print(f"{key}: {value}")
    print(f"Вероятность инсульта: {probability:.2%}")
    print("="*40)
    
    # Сохраняем в "базу" (словарь)
    fake_db[user_id] = {
        'data': data,
        'probability': probability,
    }

def get_last_user_data():
    """Для тестирования: получить последние сохраненные данные"""
    if not fake_db:
        return None
    return fake_db[next(reversed(fake_db))]