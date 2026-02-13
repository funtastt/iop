"""
Веб-краулер для скачивания HTML-страниц.

Модуль реализует краулер, который загружает HTML-страницы по списку URL-адресов
и сохраняет их в локальную директорию для последующей обработки поисковой системой.

Авторы:
    Асадуллин Салават Рустамович, группа 11-201, 4 курс
    Лобанов Никита Михайлович, группа 11-201, 4 курс

Курс: Основы информационного поиска
Итерация 1: Веб-краулер
"""

import os
import time
import logging
import requests

# ============================================================
# Настройка логирования
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),                          # Вывод в консоль
        logging.FileHandler("crawler.log", encoding="utf-8"),  # Запись в файл
    ],
)
logger = logging.getLogger(__name__)

# ============================================================
# Константы
# ============================================================
URLS_FILE = "urls_list.txt"       # Файл со списком URL-адресов
PAGES_DIR = "pages"               # Директория для сохранения страниц
INDEX_FILE = "index.txt"          # Индексный файл (номер -> URL)
REQUEST_TIMEOUT = 15              # Таймаут HTTP-запроса в секундах
DELAY_BETWEEN_REQUESTS = 0.5     # Задержка между запросами (секунды)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def load_urls(filename: str) -> list[str]:
    """
    Загрузка списка URL-адресов из текстового файла.

    Каждая непустая строка файла считается отдельным URL.
    Пустые строки и строки-комментарии (начинающиеся с #) пропускаются.

    Args:
        filename: Путь к файлу со списком URL.

    Returns:
        Список URL-адресов.
    """
    if not os.path.exists(filename):
        logger.error("Файл со списком URL не найден: %s", filename)
        return []

    urls = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Пропускаем пустые строки и комментарии
            if line and not line.startswith("#"):
                urls.append(line)

    logger.info("Загружено %d URL из файла %s", len(urls), filename)
    return urls


def get_already_downloaded() -> set[int]:
    """
    Определение уже скачанных страниц по существующему индексному файлу.

    Позволяет продолжить скачивание с места остановки при повторном запуске.

    Returns:
        Множество номеров уже скачанных страниц.
    """
    downloaded = set()
    if not os.path.exists(INDEX_FILE):
        return downloaded

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    num = int(line.split(maxsplit=1)[0])
                    downloaded.add(num)
                except (ValueError, IndexError):
                    continue

    logger.info("Обнаружено %d ранее скачанных страниц", len(downloaded))
    return downloaded


def download_page(url: str) -> str | None:
    """
    Скачивание одной HTML-страницы по указанному URL.

    Выполняет HTTP GET-запрос с установленным User-Agent и таймаутом.
    При ошибке возвращает None и логирует причину.

    Args:
        url: URL-адрес страницы для скачивания.

    Returns:
        HTML-содержимое страницы или None при ошибке.
    """
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()  # Проверяем код ответа (200 OK)

        # Проверяем, что ответ содержит HTML
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            logger.warning("Страница не является HTML (%s): %s", content_type, url)
            return None

        return response.text

    except requests.exceptions.Timeout:
        logger.error("Таймаут при загрузке: %s", url)
    except requests.exceptions.ConnectionError:
        logger.error("Ошибка соединения: %s", url)
    except requests.exceptions.HTTPError as e:
        logger.error("HTTP-ошибка %s: %s", e.response.status_code, url)
    except requests.exceptions.RequestException as e:
        logger.error("Непредвиденная ошибка при загрузке %s: %s", url, e)

    return None


def save_page(content: str, page_number: int) -> str:
    """
    Сохранение HTML-содержимого страницы в файл.

    Страница сохраняется в директорию PAGES_DIR с именем вида page_NNN.html,
    где NNN — порядковый номер с ведущими нулями.

    Args:
        content: HTML-содержимое страницы.
        page_number: Порядковый номер страницы.

    Returns:
        Путь к сохранённому файлу.
    """
    filename = f"page_{page_number:03d}.html"
    filepath = os.path.join(PAGES_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath


def append_to_index(page_number: int, url: str) -> None:
    """
    Добавление записи в индексный файл.

    Каждая запись содержит номер страницы и соответствующий URL,
    разделённые пробелом.

    Args:
        page_number: Номер страницы.
        url: URL-адрес страницы.
    """
    with open(INDEX_FILE, "a", encoding="utf-8") as f:
        f.write(f"{page_number} {url}\n")


def main() -> None:
    """
    Основная функция краулера.

    Выполняет следующие шаги:
    1. Создаёт директорию для страниц (если не существует).
    2. Загружает список URL из файла.
    3. Определяет уже скачанные страницы (для продолжения работы).
    4. Последовательно скачивает каждую страницу с задержкой.
    5. Сохраняет страницы и обновляет индексный файл.
    6. Выводит итоговую статистику.
    """
    logger.info("=" * 60)
    logger.info("Запуск веб-краулера")
    logger.info("=" * 60)

    # Создаём директорию для страниц
    os.makedirs(PAGES_DIR, exist_ok=True)

    # Загружаем список URL
    urls = load_urls(URLS_FILE)
    if not urls:
        logger.error("Список URL пуст. Завершение работы.")
        return

    # Определяем, какие страницы уже скачаны
    already_downloaded = get_already_downloaded()

    # Счётчики для статистики
    success_count = 0
    error_count = 0
    skip_count = 0

    # Основной цикл скачивания
    for i, url in enumerate(urls, start=1):
        # Пропускаем уже скачанные страницы
        if i in already_downloaded:
            logger.info("[%d/%d] Пропуск (уже скачано): %s", i, len(urls), url)
            skip_count += 1
            continue

        logger.info("[%d/%d] Скачивание: %s", i, len(urls), url)

        # Скачиваем страницу
        content = download_page(url)

        if content is not None:
            # Сохраняем страницу в файл
            filepath = save_page(content, i)
            # Добавляем запись в индекс
            append_to_index(i, url)
            success_count += 1
            logger.info("  -> Сохранено: %s (%d символов)", filepath, len(content))
        else:
            error_count += 1
            logger.warning("  -> Не удалось скачать")

        # Задержка между запросами, чтобы не перегружать сервер
        if i < len(urls):
            time.sleep(DELAY_BETWEEN_REQUESTS)

    # Итоговая статистика
    logger.info("=" * 60)
    logger.info("Краулинг завершён!")
    logger.info("  Всего URL:      %d", len(urls))
    logger.info("  Скачано:         %d", success_count)
    logger.info("  Пропущено:       %d", skip_count)
    logger.info("  Ошибок:          %d", error_count)
    logger.info("  Файлы в:         %s/", PAGES_DIR)
    logger.info("  Индекс:          %s", INDEX_FILE)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
