# ai_gigachat.py
from gigachat import GigaChat

def connect_gigachat(credentials: str, verify_ssl_certs: bool = True) -> GigaChat:
    """
    Подключается к API GigaChat с использованием переданных учетных данных.
    
    Параметры:
    credentials (str): Строка с учетными данными (токен авторизации)
    verify_ssl_certs (bool): Проверять SSL сертификаты (по умолчанию True)
    
    Возвращает:
    GigaChat: Объект для взаимодействия с API GigaChat
    """
    try:
        # Создаем подключение с использованием токена
        giga = GigaChat(
            credentials=credentials,
            verify_ssl_certs=False,  # Отключаем проверку SSL
            model="GigaChat:latest"  # Используем последнюю версию модели
        )
        print("Успешное подключение к GigaChat API")
        return giga
    except Exception as e:
        print(f"Ошибка подключения к GigaChat API: {e}")
        raise

def ask_gigachat(giga: GigaChat, prompt: str) -> str:
    """
    Отправляет запрос в GigaChat и возвращает ответ.
    
    Параметры:
    giga (GigaChat): Объект подключения к API
    prompt (str): Текст запроса (промпт)
    
    Возвращает:
    str: Ответ от языковой модели
    """
    try:
        # Отправляем запрос (без параметра temperature)
        response = giga.chat(prompt)
        return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка при запросе к GigaChat: {e}")
        raise

def create_summary_prompt(article_text: str) -> str:
    """
    Создает промпт для саммаризации научной статьи.
    
    Параметры:
    article_text (str): Текст научной статьи
    
    Возвращает:
    str: Готовый промпт для отправки в модель
    """
    return f"""
    Пожалуйста, сделай качественную саммаризацию следующей научной статьи.
    Саммари должна быть на русском языке и содержать:
    1. Основную цель исследования
    2. Методологию
    3. Ключевые результаты
    4. Выводы и значение работы
    
    Текст статьи:
    {article_text}
    
    Соблюдай научный стиль изложения и будь точным в передаче информации.
    Объем саммари - не более 20% от оригинального текста.
    """

if __name__ == "__main__":
    # Замените на ваш реальный токен
    GIGACHAT_CREDENTIALS = "ZDBjMjE4N2QtMTZmNC00NjQxLWJlMTAtMTNjOGI4MWJmNjRmOmIzOTg0MjU2LWU1MDItNDFjNi05ODViLWNkMzNiZWIyMmJkMg=="
    
    # Пример научной статьи (в реальности это будет полный текст)
    scientific_article = """
    В последние годы искусственный интеллект стал важным инструментом в медицинской диагностике.
    В данной работе мы представляем новый метод анализа рентгеновских снимков с использованием
    глубоких нейронных сетей. Наша модель, основанная на архитектуре ResNet-152, демонстрирует
    точность 98.7% в обнаружении ранних признаков пневмонии, что на 12% превышает показатели
    предыдущих методов. Исследование проводилось на выборке из 15,000 снимков из 5 медицинских
    центров. Результаты показывают, что предложенный подход может значительно улучшить раннюю
    диагностику респираторных заболеваний.
    """
    
    try:
        # Подключаемся к API
        giga_connection = connect_gigachat(GIGACHAT_CREDENTIALS)
        
        # Создаем промпт для саммаризации
        prompt = create_summary_prompt(scientific_article)
        
        # Получаем саммари
        summary = ask_gigachat(giga_connection, prompt)
        
        print("\nОригинальный текст статьи:")
        print(scientific_article)
        
        print("\nСгенерированная саммари:")
        print(summary)
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")