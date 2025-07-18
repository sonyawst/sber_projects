import requests
from urllib.parse import urlparse
from gigachat import GigaChat
from typing import Optional
import arxiv

class NotAvailable(Exception):
    """Исключение для недоступных статей"""
    pass

class Summarizer:
    def __init__(self, giga_token: str):
        """Инициализация с подключением к GigaChat"""
        try:
            self.giga = GigaChat(
                credentials=giga_token,
                verify_ssl_certs=False,  # Для тестового режима
                model="GigaChat:latest"
            )
            print("Успешное подключение к GigaChat API")
        except Exception as e:
            print(f"Ошибка подключения к GigaChat: {e}")
            raise

    def __article_to_text(self, link: str) -> str:
        """
        Приватный метод загрузки текста статьи (первые 3000 символов)
        
        Аргументы:
            link: Ссылка на статью в arXiv
            
        Возвращает:
            str: Текст статьи (не более 3000 символов)
            
        Исключения:
            NotAvailable: Если статья недоступна
        """
        try:
            # Извлекаем ID статьи
            arxiv_id = self.__extract_arxiv_id(link)
            
            # Получаем метаданные через arXiv API
            search = arxiv.Search(id_list=[arxiv_id])
            paper = next(search.results(), None)
            
            if not paper:
                raise NotAvailable("Статья не найдена")
            
            # Формируем базовую информацию
            base_text = f"""
Название: {paper.title}
Авторы: {', '.join(a.name for a in paper.authors)}
Дата: {paper.published.strftime('%Y-%m-%d')}
Аннотация: {paper.summary}
"""
            
            # Если есть PDF - загружаем первые страницы
            if paper.pdf_url:
                try:
                    response = requests.get(paper.pdf_url)
                    response.raise_for_status()
                    
                    # Извлекаем текст из первых 3 страниц PDF
                    from PyPDF2 import PdfReader
                    from io import BytesIO
                    
                    pdf_text = ""
                    with BytesIO(response.content) as f:
                        reader = PdfReader(f)
                        for i, page in enumerate(reader.pages):
                            if i >= 3:  # Ограничиваем количеством страниц
                                break
                            pdf_text += page.extract_text() + "\n"
                    
                    full_text = base_text + "\nТекст статьи:\n" + pdf_text
                    return full_text[:3000]  # Обрезаем до 3000 символов
                
                except Exception:
                    return base_text[:3000]
            
            return base_text[:3000]
            
        except Exception as e:
            raise NotAvailable(f"Ошибка загрузки статьи: {str(e)}")

    def __extract_arxiv_id(self, link: str) -> str:
        """Извлекает arXiv ID из URL"""
        parsed = urlparse(link)
        if not parsed.netloc.endswith('arxiv.org'):
            raise ValueError("Некорректная ссылка arXiv")
        
        if '/abs/' in link:
            return link.split('/abs/')[-1]
        elif '/pdf/' in link:
            return link.split('/pdf/')[-1].replace('.pdf', '')
        else:
            raise ValueError("Неподдерживаемый формат ссылки arXiv")

    def __send_gigachat(self, text: str) -> str:
        """
        Приватный метод отправки текста в GigaChat
        
        Аргументы:
            text: Текст для обработки
            
        Возвращает:
            str: Ответ модели
        """
        try:
            # Оптимальный промпт для научной саммаризации
            prompt = f"""
Сделай качественную саммаризацию научной статьи на русском языке. 
Соблюдай структуру:
1. Основная цель исследования
2. Использованные методы
3. Ключевые результаты
4. Значение и перспективы работы

Текст статьи:
{text}

Соблюдай научный стиль, будь точным и сохраняй важные детали. 
Объем саммари - около 15-20% от исходного текста.
"""
            response = self.giga.chat(prompt)
            return response.choices[0].message.content
        except Exception as e:
            print(f"Ошибка запроса к GigaChat: {e}")
            raise

    def summarize(self, link: str) -> str:
        """
        Публичный метод для получения саммари статьи
        
        Аргументы:
            link: Ссылка на статью в arXiv
            
        Возвращает:
            str: Краткое содержание на русском
        """
        try:
            print(f"Обработка статьи: {link}")
            article_text = self.__article_to_text(link)
            print(f"Загружен текст ({len(article_text)} символов)")
            
            summary = self.__send_gigachat(article_text)
            return summary
            
        except NotAvailable as e:
            return f"Ошибка: {str(e)}"
        except Exception as e:
            return f"Неожиданная ошибка: {str(e)}"

# Пример использования
if __name__ == "__main__":
    # Ваш токен GigaChat
    GIGA_TOKEN = "ZDBjMjE4N2QtMTZmNC00NjQxLWJlMTAtMTNjOGI4MWJmNjRmOmIzOTg0MjU2LWU1MDItNDFjNi05ODViLWNkMzNiZWIyMmJkMg=="
    
    # Пример статьи по машинному обучению
    TEST_ARTICLE = "https://arxiv.org/abs/2106.04562"
    
    try:
        summarizer = Summarizer(GIGA_TOKEN)
        result = summarizer.summarize(TEST_ARTICLE)
        
        print("\nРезультат саммаризации:")
        print(result)
        
    except Exception as e:
        print(f"Критическая ошибка: {e}")