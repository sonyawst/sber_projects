from __future__ import annotations

import argparse
import sys
from pathlib import Path


#  Импорт класса Summarizer

try:
    from summarizer import Summarizer
except ModuleNotFoundError:
    # добавляем путь проекта.
    PROJECT_ROOT = Path(__file__).resolve().parent
    sys.path.insert(0, str(PROJECT_ROOT))
    from summarizer import Summarizer  


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Скачивает статью с arXiv, отправляет первые 3000 символов в GigaChat "
            "и дает краткое содержание на русском языке."
        )
    )
    parser.add_argument(
        "link",
        help="Ссылка вида https://arxiv.org/abs/<id> | https://arxiv.org/pdf/<id>.pdf | "
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summarizer = Summarizer()

    try:
        summary = summarizer.summarize(args.link)
    except KeyboardInterrupt:
        print("\nРабота прервана пользователем.", file=sys.stderr)
        sys.exit(130)
    except Exception as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        sys.exit(1)

    # --- выводим результат ---
    print("\n----- Краткое содержание -----\n")
    print(summary)


if __name__ == "__main__":
    main()
