import telebot
from telebot import types
import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = telebot.TeleBot('7223296971:AAEAb-QM30d2ojt6_db6NyUWX9Qaxl7uqq8')

# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect('my_database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Получение списка исследований из БД
def get_available_trials():
    conn = get_db_connection()
    trials = conn.execute('SELECT trial_id, trial_name, med FROM trials').fetchall()
    conn.close()
    
    trials_dict = {}
    for trial in trials:
        trials_dict[trial['trial_name']] = {
            'id': trial['trial_id'],
            'med': trial['med'],
            'drugs': ['Плацебо', trial['med']]
        }
    return trials_dict

# Функция для сохранения данных в БД
def save_measurement_to_db(data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Получаем максимальный measurement_id и увеличиваем на 1
        cursor.execute("SELECT MAX(measurement_id) FROM measurements")
        max_id = cursor.fetchone()[0]
        new_id = (max_id or 0) + 1
        
        # Вставляем новую запись
        cursor.execute("""
            INSERT INTO measurements 
            (measurement_id, patient_id, trial_id, measurement_date, drug, condition_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            new_id,
            data['id'],
            data['trial_id'],
            datetime.now().strftime('%Y-%m-%d'),
            data['drug'],
            data['condition']
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logging.error(f"Ошибка при сохранении данных: {e}")
        return False

# Функция для анализа данных
def analyze_condition(trial_id, drug, user_condition):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Получаем среднее значение condition_score для данного препарата в исследовании
        cursor.execute("""
            SELECT AVG(condition_score) as avg_score
            FROM measurements
            WHERE trial_id = ? AND drug = ?
        """, (trial_id, drug))
        
        result = cursor.fetchone()
        avg_score = result['avg_score'] if result['avg_score'] is not None else 50  # Значение по умолчанию, если данных нет
        
        # Рассчитываем диапазон нормы (±10% от среднего)
        lower_bound = avg_score * 0.9
        upper_bound = avg_score * 1.1
        
        # Определяем, входит ли оценка пользователя в диапазон нормы
        within_range = lower_bound <= user_condition <= upper_bound
        
        conn.close()
        
        return {
            'avg_score': round(avg_score, 1),
            'lower_bound': round(lower_bound, 1),
            'upper_bound': round(upper_bound, 1),
            'within_range': within_range
        }
    except Exception as e:
        logging.error(f"Ошибка при анализе данных: {e}")
        return None

# Хранение временных данных пользователя
user_data = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_data[message.chat.id] = {}
    msg = bot.send_message(message.chat.id, "Добро пожаловать в систему клинических исследований! Введите ваш ID (положительное число):")
    bot.register_next_step_handler(msg, process_id_step)

def process_id_step(message):
    try:
        chat_id = message.chat.id
        user_id = int(message.text)
        
        if user_id <= 0:
            raise ValueError("ID должен быть положительным числом")
            
        user_data[chat_id]['id'] = user_id
        
        # Проверяем существование пациента в БД
        conn = get_db_connection()
        patient = conn.execute('SELECT * FROM patients WHERE patient_id = ?', (user_id,)).fetchone()
        conn.close()
        
        if not patient:
            msg = bot.send_message(chat_id, "Пациент с таким ID не найден в базе данных. Введите другой ID:")
            bot.register_next_step_handler(msg, process_id_step)
            return
            
        # Получаем актуальный список исследований из БД
        trials = get_available_trials()
        user_data[chat_id]['trials'] = trials
        
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for trial_name in trials.keys():
            markup.add(trial_name)
            
        msg = bot.send_message(chat_id, "Выберите исследование из списка:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_trial_step)
        
    except ValueError:
        msg = bot.send_message(message.chat.id, "Ошибка: ID должен быть положительным целым числом. Пожалуйста, введите корректный ID:")
        bot.register_next_step_handler(msg, process_id_step)

def process_trial_step(message):
    chat_id = message.chat.id
    trials = user_data[chat_id]['trials']
    
    if message.text not in trials:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for trial_name in trials.keys():
            markup.add(trial_name)
            
        msg = bot.send_message(chat_id, "Пожалуйста, выберите исследование из предложенного списка:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_trial_step)
        return
    
    user_data[chat_id]['trial'] = message.text
    user_data[chat_id]['trial_id'] = trials[message.text]['id']
    user_data[chat_id]['trial_drugs'] = trials[message.text]['drugs']
    
    msg = bot.send_message(chat_id, "Оцените ваше самочувствие по шкале от 0 до 100:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, process_condition_step)

def process_condition_step(message):
    try:
        chat_id = message.chat.id
        condition = int(message.text)
        
        if condition < 0 or condition > 100:
            raise ValueError("Оценка должна быть от 0 до 100")
            
        user_data[chat_id]['condition'] = condition
        
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for drug in user_data[chat_id]['trial_drugs']:
            markup.add(drug)
            
        msg = bot.send_message(chat_id, "Выберите принимаемый препарат:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_drug_step)
        
    except ValueError:
        msg = bot.send_message(message.chat.id, "Ошибка: оценка самочувствия должна быть целым числом от 0 до 100. Пожалуйста, введите корректное значение:")
        bot.register_next_step_handler(msg, process_condition_step)

def process_drug_step(message):
    chat_id = message.chat.id
    trial_name = user_data[chat_id]['trial']
    trial_id = user_data[chat_id]['trial_id']
    trial_drugs = user_data[chat_id]['trial_drugs']
    
    if message.text not in trial_drugs:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for drug in trial_drugs:
            markup.add(drug)
            
        msg = bot.send_message(chat_id, f"Пожалуйста, выберите препарат из предложенных для исследования {trial_name}:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_drug_step)
        return
    
    user_data[chat_id]['drug'] = message.text
    
    # Сохраняем данные в БД
    save_success = save_measurement_to_db(user_data[chat_id])
    
    # Анализируем данные
    analysis = analyze_condition(
        trial_id=user_data[chat_id]['trial_id'],
        drug=user_data[chat_id]['drug'],
        user_condition=user_data[chat_id]['condition']
    )
    
    # Формируем ответ пользователю
    response_parts = [
        f"Спасибо! Вот ваши данные:\n\n"
        f"ID пациента: {user_data[chat_id]['id']}\n"
        f"Исследование: {trial_name}\n"
        f"Препарат: {user_data[chat_id]['drug']}\n"
        f"Ваша оценка самочувствия: {user_data[chat_id]['condition']}/100\n\n"
    ]
    
    if analysis:
        response_parts.append(
            f"Статистика по препарату в этом исследовании:\n"
            f"Средний показатель: {analysis['avg_score']}\n"
            f"Диапазон нормы: от {analysis['lower_bound']} до {analysis['upper_bound']}\n\n"
        )
        
        if analysis['within_range']:
            response_parts.append("✅ Ваше самочувствие находится в пределах нормы для этого препарата.")
        else:
            if user_data[chat_id]['condition'] < analysis['lower_bound']:
                response_parts.append("⚠️ Ваше самочувствие ниже нормы для этого препарата.")
            else:
                response_parts.append("⚠️ Ваше самочувствие выше нормы для этого препарата.")
    else:
        response_parts.append("Не удалось проанализировать данные. Пожалуйста, обратитесь к администратору.")
    
    if save_success:
        response_parts.append("\n\nДанные успешно сохранены в базу данных.")
    else:
        response_parts.append("\n\n⚠️ Не удалось сохранить данные в базу данных.")
    
    bot.send_message(chat_id, "".join(response_parts), reply_markup=types.ReplyKeyboardRemove())
    del user_data[chat_id]

@bot.message_handler(commands=['cancel'])
def cancel_handler(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        del user_data[chat_id]
    bot.send_message(chat_id, "Ввод данных отменен. Все временные данные удалены.", reply_markup=types.ReplyKeyboardRemove())

if __name__ == '__main__':
    print("Бот клинических исследований запущен и готов к работе...")
    bot.polling(none_stop=True, skip_pending=True)