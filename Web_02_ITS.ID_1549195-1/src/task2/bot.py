import telebot
from telebot import types


# Инициализация бота
bot = telebot.TeleBot('7223296971:AAEAb-QM30d2ojt6_db6NyUWX9Qaxl7uqq8')

# Словарь исследований и соответствующих препаратов
AVAILABLE_TRIALS = {
    "Исследование эффективности Атропина": ["Плацебо", "Атропин"],
    "Клинические испытания Бисопролола": ["Плацебо", "Бисопролол"],
    "Изучение воздействия Ибупрофена": ["Плацебо", "Ибупрофен"],
    "Тестирование Аторвастатина": ["Плацебо", "Аторвастатин"],
    "Оценка эффективности Добутамина": ["Плацебо", "Добутамин"],
    "Исследование Ацетилцистеина": ["Плацебо", "Ацетилцистеин"]
}

# Хранение временных данных пользователя
user_data = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # Очищаем предыдущие данные пользователя
    user_data[message.chat.id] = {}
    
    # Запрашиваем ID
    msg = bot.send_message(message.chat.id, "Добро пожаловать в систему клинических исследований! Пожалуйста, введите ваш ID (положительное число):")
    bot.register_next_step_handler(msg, process_id_step)

def process_id_step(message):
    try:
        chat_id = message.chat.id
        user_id = int(message.text)
        
        if user_id <= 0:
            raise ValueError("ID должен быть положительным числом")
            
        # Сохраняем ID
        user_data[chat_id]['id'] = user_id
        
        # Создаем клавиатуру с исследованиями
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for trial in AVAILABLE_TRIALS.keys():
            markup.add(trial)
            
        msg = bot.send_message(chat_id, "Выберите исследование из списка:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_trial_step)
        
    except ValueError:
        msg = bot.send_message(message.chat.id, "Ошибка: ID должен быть положительным целым числом. Пожалуйста, введите корректный ID:")
        bot.register_next_step_handler(msg, process_id_step)

def process_trial_step(message):
    chat_id = message.chat.id
    
    # Проверяем, что выбрано существующее исследование
    if message.text not in AVAILABLE_TRIALS:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for trial in AVAILABLE_TRIALS.keys():
            markup.add(trial)
            
        msg = bot.send_message(chat_id, "Пожалуйста, выберите исследование из предложенного списка:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_trial_step)
        return
    
    # Сохраняем исследование
    user_data[chat_id]['trial'] = message.text
    
    # Запрашиваем оценку самочувствия
    msg = bot.send_message(chat_id, "Оцените ваше самочувствие по шкале от 0 до 100:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, process_condition_step)

def process_condition_step(message):
    try:
        chat_id = message.chat.id
        
        # Проверяем, что оценка в диапазоне 0-100
        condition = int(message.text)
        if condition < 0 or condition > 100:
            raise ValueError("Оценка должна быть от 0 до 100")
            
        # Сохраняем оценку
        user_data[chat_id]['condition'] = condition
        
        # Создаем клавиатуру с препаратами для выбранного исследования
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for drug in AVAILABLE_TRIALS[user_data[chat_id]['trial']]:
            markup.add(drug)
            
        msg = bot.send_message(chat_id, "Выберите принимаемый препарат:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_drug_step)
        
    except ValueError:
        msg = bot.send_message(message.chat.id, "Ошибка: оценка самочувствия должна быть целым числом от 0 до 100. Пожалуйста, введите корректное значение:")
        bot.register_next_step_handler(msg, process_condition_step)

def process_drug_step(message):
    chat_id = message.chat.id
    trial = user_data[chat_id]['trial']
    
    # Проверяем, что выбран существующий препарат для данного исследования
    if message.text not in AVAILABLE_TRIALS[trial]:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for drug in AVAILABLE_TRIALS[trial]:
            markup.add(drug)
            
        msg = bot.send_message(chat_id, f"Пожалуйста, выберите препарат из предложенных для исследования {trial}:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_drug_step)
        return
    
    # Сохраняем препарат
    user_data[chat_id]['drug'] = message.text
    
    # Анализируем данные
    condition = user_data[chat_id]['condition']
    drug = user_data[chat_id]['drug']
    
    # Определяем нормальный диапазон в зависимости от препарата
    normal_range = (40, 70) if drug == "Плацебо" else (60, 90)
    
    # Формируем анализ
    if normal_range[0] <= condition <= normal_range[1]:
        analysis = "Ваше самочувствие находится в нормальном диапазоне для этого препарата."
    else:
        analysis = "Ваше самочувствие выходит за пределы нормального диапазона для этого препарата."
    
    # Формируем итоговое сообщение
    response = (
        f"Спасибо! Вот ваши данные:\n\n"
        f"ID: {user_data[chat_id]['id']}\n"
        f"Исследование: {trial}\n"
        f"Оценка самочувствия: {condition}/100\n"
        f"Препарат: {drug}\n\n"
        f"{analysis}"
    )
    
    bot.send_message(chat_id, response, reply_markup=types.ReplyKeyboardRemove())
    
    # Очищаем данные пользователя
    del user_data[chat_id]

@bot.message_handler(commands=['cancel'])
def cancel_handler(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        del user_data[chat_id]
    bot.send_message(chat_id, "Ввод данных отменен. Все временные данные удалены.", reply_markup=types.ReplyKeyboardRemove())

if __name__ == '__main__':
    print("Бот клинических исследований запущен и готов к работе...")
    bot.polling(none_stop=True)