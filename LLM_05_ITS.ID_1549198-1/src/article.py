import requests
from urllib.parse import urlparse
from typing import Optional
import arxiv  # Официальная библиотека для работы с arXiv API

class NotAvailable(Exception):
    """Кастомное исключение для недоступных статей"""
    pass

def article_to_text(link: str) -> str:
    try:
        # Проверяем, что ссылка ведет на arXiv
        parsed_url = urlparse(link)
        if not parsed_url.netloc.endswith('arxiv.org'):
            raise ValueError("Ссылка должна вести на arxiv.org")
        
        # Извлекаем ID статьи из URL
        if '/abs/' in link:
            arxiv_id = link.split('/abs/')[-1]
        elif '/pdf/' in link:
            arxiv_id = link.split('/pdf/')[-1].replace('.pdf', '')
        else:
            raise ValueError("Неподдерживаемый формат ссылки arXiv")
        
        # Ищем статью через официальный API arXiv
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results(), None)
        
        if paper is None:
            raise NotAvailable(f"Статья {arxiv_id} не найдена на arXiv")
        
        # Скачиваем PDF (если доступен)
        if paper.pdf_url:
            try:
                response = requests.get(paper.pdf_url)
                response.raise_for_status()
                
                # Здесь можно добавить обработку PDF в текст
                # Для простоты возвращаем метаданные
                return format_article_text(paper)
            except requests.RequestException:
                raise NotAvailable(f"Не удалось загрузить PDF для статьи {arxiv_id}")
        else:
            return format_article_text(paper)
            
    except Exception as e:
        if not isinstance(e, (NotAvailable, ValueError)):
            raise NotAvailable(f"Ошибка при загрузке статьи: {str(e)}")
        raise

def format_article_text(paper: arxiv.Result) -> str:
    """
    Форматирует метаданные статьи в читаемый текст.
    """
    return f"""
Название: {paper.title}
Авторы: {', '.join(author.name for author in paper.authors)}
Дата публикации: {paper.published.strftime('%Y-%m-%d')}

Аннотация:
{paper.summary}

Ссылки:
PDF: {paper.pdf_url if paper.pdf_url else 'недоступно'}
"""

# Пример использования
if __name__ == "__main__":
    try:
        # Пример рабочей статьи по машинному обучению
        test_link = "https://arxiv.org/abs/2106.04562"
        article_text = article_to_text(test_link)
        print("Успешно загружена статья:")
        print(article_text)
        
    except NotAvailable as e:
        print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")