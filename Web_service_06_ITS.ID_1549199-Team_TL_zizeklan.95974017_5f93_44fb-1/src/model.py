from joblib import load
import pandas as pd
import os

def load_model():
    try:
        # Получаем абсолютный путь к файлу модели
        dir_path = os.path.dirname(os.path.realpath(__file__))
        model_path = os.path.join(dir_path, 'data/best_stroke_model.pkl')
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Файл модели не найден по пути: {model_path}")
            
        return load(model_path)
    except Exception as e:
        print(f"Ошибка при загрузке модели: {e}")
        raise


def predict_stroke_risk(input_data):
    """Прогнозирование риска инсульта и классификация уровня риска"""
    model = load_model()

    # Преобразование входных данных в DataFrame
    input_df = pd.DataFrame([input_data])
    
    # Предсказание вероятности
    probability = model.predict_proba(input_df)[0, 1]
    
    # Классификация уровня риска
    if probability < 0.1:
        risk_level = "Крайне низкий"
    elif probability < 0.3:
        risk_level = "Низкий"
    elif probability < 0.5:
        risk_level = "Значительный"
    elif probability < 0.7:
        risk_level = "Высокий"
    else:
        risk_level = "Крайне высокий"
    
    return probability, risk_level
