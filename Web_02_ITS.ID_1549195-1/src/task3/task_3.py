import telebot
from telebot import types
import sqlite3
import logging
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
    trial_drugs = user_data[chat_id]['trial_drugs']
    
    if message.text not in trial_drugs:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for drug in trial_drugs:
            markup.add(drug)
            
        msg = bot.send_message(chat_id, f"Пожалуйста, выберите препарат из предложенных для исследования {trial_name}:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_drug_step)
        return
    
    user_data[chat_id]['drug'] = message.text
    
    # Анализ данных
    condition = user_data[chat_id]['condition']
    drug = user_data[chat_id]['drug']
    
    normal_range = (40, 70) if drug == "Плацебо" else (60, 90)
    
    if normal_range[0] <= condition <= normal_range[1]:
        analysis = "Ваше самочувствие находится в нормальном диапазоне для этого препарата."
    else:
        analysis = "Ваше самочувствие выходит за пределы нормального диапазона для этого препарата."
    
    response = (
        f"Спасибо! Вот ваши данные:\n\n"
        f"ID: {user_data[chat_id]['id']}\n"
        f"Исследование: {trial_name}\n"
        f"Оценка самочувствия: {condition}/100\n"
        f"Препарат: {drug}\n\n"
        f"{analysis}"
    )
    
    bot.send_message(chat_id, response, reply_markup=types.ReplyKeyboardRemove())
    
    # Сохранение в БД (будет реализовано в следующих заданиях)
    # save_to_database(user_data[chat_id])
    
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
