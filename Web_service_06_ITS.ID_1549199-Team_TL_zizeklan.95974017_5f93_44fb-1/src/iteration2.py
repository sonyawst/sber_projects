import telebot
import traceback
import sys
from telebot import types
from config import BOT_TOKEN
from database import init_db, save_user_data, get_last_user_data
from model import predict_stroke_risk

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# Временное хранилище данных пользователя
user_data = {}

def safe_execute(func):
    """Декоратор для обработки ошибок"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Ошибка: {e}\n{traceback.format_exc()}")
            chat_id = args[0].chat.id if args else None
            if chat_id:
                bot.send_message(chat_id, "Упс! Возникла непредвиденная ошибка😔 Попробуйте перезапустить бота")
            sys.exit(1)  # Останавливаем бота при ошибке
    return wrapper

@safe_execute
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_male = types.KeyboardButton("Мужской")
    btn_female = types.KeyboardButton("Женский")
    markup.add(btn_male, btn_female)
    bot.send_message(
        message.chat.id,
        "Добро пожаловать! Этот бот оценивает риск развития инсульта.\n\n"
        "Выберите ваш пол:",
        reply_markup=markup
    )
    user_data[message.chat.id] = {}  # Инициализация хранилища

@safe_execute
@bot.message_handler(func=lambda message: message.text in ["Мужской", "Женский"])
def ask_age(message):
    chat_id = message.chat.id
    user_data[chat_id]["gender"] = "Male" if message.text == "Мужской" else "Female"
    
    markup = types.ReplyKeyboardRemove()  # Убираем кнопки
    bot.send_message(
        chat_id,
        "Введите ваш возраст (целое число):",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, ask_hypertension)

@safe_execute
def ask_hypertension(message):
    chat_id = message.chat.id
    try:
        age = int(message.text)
        if age < 0 or age > 99:
            raise ValueError
        user_data[chat_id]["age"] = age
    except ValueError:
        bot.send_message(chat_id, "Пожалуйста, введите корректный возраст!")
        return bot.register_next_step_handler(message, ask_hypertension)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_yes = types.KeyboardButton("Да")
    btn_no = types.KeyboardButton("Нет")
    markup.add(btn_yes, btn_no)
    
    bot.send_message(
        chat_id,
        "Диагностирована ли у вас гипертензия/гипертоническая болезнь?",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, ask_heart_disease)

@safe_execute
def ask_heart_disease(message):
    chat_id = message.chat.id
    user_data[chat_id]["hypertension"] = 1 if message.text == "Да" else 0
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_yes = types.KeyboardButton("Да")
    btn_no = types.KeyboardButton("Нет")
    markup.add(btn_yes, btn_no)
    
    bot.send_message(
        chat_id,
        "Есть ли у вас диагностированные болезни сердечно-сосудистой системы?",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, ask_married)

@safe_execute
def ask_married(message):
    chat_id = message.chat.id
    user_data[chat_id]["heart_disease"] = 1 if message.text == "Да" else 0
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_yes = types.KeyboardButton("Да")
    btn_no = types.KeyboardButton("Нет")
    markup.add(btn_yes, btn_no)
    
    bot.send_message(
        chat_id,
        "Вы женаты/замужем?",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, ask_work)

@safe_execute
def ask_work(message):
    chat_id = message.chat.id
    user_data[chat_id]["ever_married"] = 1 if message.text == "Да" else 0
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_self = types.KeyboardButton("1")
    btn_private = types.KeyboardButton("2")
    btn_govt = types.KeyboardButton("3")
    btn_unemployed = types.KeyboardButton("4")
    markup.add(btn_self, btn_private, btn_govt, btn_unemployed)
    
    bot.send_message(
        chat_id,
        "Укажите вашу профессиональную принадлежность:\n"
        "1 - Работаю на себя\n"
        "2 - Работаю в частной фирме\n"
        "3 - Работаю в государственном учреждении\n"
        "4 - Кайфую (не работаю)",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, ask_residence)

@safe_execute
def ask_residence(message):
    chat_id = message.chat.id
    work_type_map = {
        "1": "Self-employed",
        "2": "Private",
        "3": "Govt_job",
        "4": "Unemployed"
    }
    user_data[chat_id]["work_type"] = work_type_map.get(message.text)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_urban = types.KeyboardButton("В городе")
    btn_rural = types.KeyboardButton("В сельской местности")
    markup.add(btn_urban, btn_rural)
    
    bot.send_message(
        chat_id,
        "Укажите, где вы проживаете:",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, ask_glucose)

@safe_execute
def ask_glucose(message):
    chat_id = message.chat.id
    user_data[chat_id]["Residence_type"] = 1 if message.text == "В городе" else 0
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_unknown = types.KeyboardButton("Не знаю")
    markup.add(btn_unknown)
    
    bot.send_message(
        chat_id,
        "Введите уровень глюкозы в крови (в формате 3.3). Если исследование не проводилось, нажмите «Не знаю»:",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, ask_bmi)

@safe_execute
def ask_bmi(message):
    chat_id = message.chat.id
    if message.text == "Не знаю":
        user_data[chat_id]["avg_glucose_level"] = None
    else:
        try:
            glucose = float(message.text)
            if glucose < 0 or glucose > 30:
                raise ValueError
            user_data[chat_id]["avg_glucose_level"] = glucose
        except ValueError:
            bot.send_message(chat_id, "Пожалуйста, введите корректное число! Убедитесь, что записываете число с точкой, а не запятой.")
            return bot.register_next_step_handler(message, ask_bmi)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_unknown = types.KeyboardButton("Не знаю")
    markup.add(btn_unknown)
    
    bot.send_message(
        chat_id,
        "Введите ваш ИМТ (индекс массы тела) в формате 21 или 21.3 либо нажмите «Не знаю»:",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, ask_smoking)

@safe_execute
def ask_smoking(message):
    chat_id = message.chat.id
    if message.text == "Не знаю":
        user_data[chat_id]["bmi"] = None
    else:
        try:
            bmi = float(message.text)
            if bmi < 10 or bmi > 50:
                raise ValueError
            user_data[chat_id]["bmi"] = bmi
        except ValueError:
            bot.send_message(chat_id, "Пожалуйста, введите корректное число! Убедитесь, что записываете число с точкой, а не запятой.")
            return bot.register_next_step_handler(message, ask_bmi)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_yes = types.KeyboardButton("Да")
    btn_no = types.KeyboardButton("Нет")
    btn_former = types.KeyboardButton("Раньше курил")
    markup.add(btn_yes, btn_no, btn_former)
    
    bot.send_message(
        chat_id,
        "Курите ли вы?",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, process_results)

@safe_execute
def process_results(message):
    chat_id = message.chat.id
    user_data[chat_id]["smoking_status"] = (
        "smokes" if message.text == "Да" else ("never smoked" if message.text == "Нет" else "formerly smoked")
    )
    
    # Формируем данные для модели
    data = {
        "gender": user_data[chat_id]["gender"],
        "age": user_data[chat_id]["age"],
        "hypertension": user_data[chat_id]["hypertension"],
        "heart_disease": user_data[chat_id]["heart_disease"],
        "ever_married": user_data[chat_id]["ever_married"],
        "work_type": user_data[chat_id]["work_type"],
        "Residence_type": user_data[chat_id]["Residence_type"],
        "avg_glucose_level": user_data[chat_id].get("avg_glucose_level"),
        "bmi": user_data[chat_id].get("bmi"),
        "smoking_status": user_data[chat_id]["smoking_status"],
    }
    
    # Предсказание модели 
    probability, risk_level = predict_stroke_risk(data)
    
    # Сохранение в базу данных (потом тут мб поменять надо)
    save_user_data(chat_id, data, probability)
    
    # Отправка результата
    response = (
        f"🔍 Результаты оценки риска инсульта:\n\n"
        f"• Вероятность: {probability*100:.1f}%\n"
        f"• Уровень риска: {risk_level}\n\n"
    )
    
    if risk_level in ["Высокий", "Крайне высокий"]:
        response += "❗ Срочно обратитесь к врачу для дополнительного обследования!\n"
    elif risk_level == "Значительный":
        response += "⚠ Рекомендуется консультация специалиста в ближайшее время.\n"
    else:
        response += "✅ Ваш риск в пределах нормы, но регулярные проверки здоровья важны.\n"
        
    response += "\n🔹 Персональные рекомендации:\n"
    if data.get("hypertension") == 1:
            response += ("📌 У вас гипертензия.\n"
                       "  - Ограничьте потребление соли до 3-5 г/сутки\n"
                       "  - Принимайте назначенные препараты строго по схеме\n"
                       "  - Регулярно посещайте кардиолога (минимум 2 раза в год)\n\n")
        
    if data.get("heart_disease") == 1:
        response += ("🫀 У вас болезни сердечно-сосудистой системы. Важно:\n"
                    "  - Проходить ЭКГ-мониторинг 1 раз в 3 месяца\n"
                    "  - Вести дневник давления и пульса\n"
                    "  - Избегать стрессовых ситуаций\n"
                    "  - Иметь при себе нитроглицерин (если назначен врачом)\n\n")    
    # 1. Проверка уровня глюкозы
    if data.get("avg_glucose_level") is not None and data.get("avg_glucose_level") > 5.5:
        response += ("👀 Вижу, у вас повышен уровень глюкозы (норма 3.3-5.5). Рекомендуется:\n"
                    "  - Снизить потребление сахара и быстрых углеводов\n"
                    "  - Увеличить физическую активность\n"
                    "  - Проконсультироваться с эндокринологом\n\n")
    elif data.get("avg_glucose_level") is None:
        response += "👀 Уровень глюкозы не указан. Рекомендуем проверить его при ближайшем визите к врачу.\n\n"
    
    # 2. Проверка курения
    if data.get("smoking_status") == "smokes":
        response += ("🫁 Курение - серьезный фактор риска не только инсульта, но и многих заболеваний.\n" 
                    "  - Рекомендуем книгу Аллена Карра 'Лёгкий способ бросить курить'\n"
                    "  - Если вы испытываете тревожность, обратитесь за психологической помощью\n\n")
    elif data.get("smoking_status") == "formerly smoked":
        response += "🥳 Круто, что вы бросили курить! Продолжайте в том же духе!\n\n"
    
    # 3. Проверка ИМТ
    if data.get("bmi") is not None and data.get("bmi") > 25:
        response += ("😔 Кажется, у вас избыточный вес. Рекомендуем:\n"
                    "  - Сбалансированное питание с дефицитом калорий\n"
                    "  - Регулярные занятия любым видом спорта\n"
                    "  - Консультацию диетолога\n\n")
    elif data.get("bmi") is None:
        response += "🔍 ИМТ не указан. Рекомендуем измерить рост и вес и воспользоваться калькулятором для расчета.\n\n"
    
    # 4. Проверка места жительства
    if data.get("Residence_type") == 1:
        response += ("😉 Жить в городе, конечно, удобно, но убедитесь, что вы проводите достаточно времени на свежем воздухе:\n"
                    "  - Почаще гуляйте в парках\n"
                    "  - Используйте выходные для выезда на природу\n"
                    "  - Отдавайте предпочтение пешим прогулкам\n\n")
    else:
        response += "🤩 Вау, круто, что вы живете в сельской местности! Используйте преимущества свежего воздуха для активного отдыха.\n\n"
    
    # Дополнительные общие рекомендации
    response += ("💡 Общие советы для снижения риска:\n"
                "- Контролируйте артериальное давление\n"
                "- Поддерживайте физическую активность\n"
                "- Соблюдайте сбалансированную диету\n"
                "- Ограничьте потребление алкоголя\n"
                "- Устраните по возможности источники стресса\n"
                "- Регулярно проходите медицинские осмотры\n")
    
    bot.send_message(
        chat_id,
        response,
        reply_markup=types.ReplyKeyboardRemove()
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_new = types.KeyboardButton("Лесгоооо")
    btn_exit = types.KeyboardButton("Нет")
    markup.add(btn_new, btn_exit)

    bot.send_message(
        chat_id,
        "Хотите сделать новую запись?",
        reply_markup=markup
    )

@safe_execute
@bot.message_handler(func=lambda message: message.text == "Лесгоооо")
def new_record(message):
    """Обработчик для создания новой записи"""
    chat_id = message.chat.id
    
    # Очищаем предыдущие данные пользователя
    if chat_id in user_data:
        del user_data[chat_id]
    
    # Создаем новую запись
    user_data[chat_id] = {}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_male = types.KeyboardButton("Мужской")
    btn_female = types.KeyboardButton("Женский")
    markup.add(btn_male, btn_female)
    
    bot.send_message(
        chat_id,
        "Хорошо!\n\n"
        "Выберите ваш пол:",
        reply_markup=markup
    )

@safe_execute
@bot.message_handler(func=lambda message: message.text == "Нет")
def exit_bot(message):
    """Обработчик для завершения работы"""
    chat_id = message.chat.id
    if chat_id in user_data:
        del user_data[chat_id]
    
    bot.send_message(
        chat_id,
        "Спасибо за использование бота! Для нового опроса используйте /start",
        reply_markup=types.ReplyKeyboardRemove()
    )
    raise SystemExit


if __name__ == "__main__":
    init_db()  # Инициализация БД
    get_last_user_data() # потом надо убрать
    print('Бот запущен...')
    bot.polling(none_stop=True)