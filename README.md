**Авторы:**
- Асадуллин Салават Рустамович, группа 11-201, 4 курс
- Лобанов Никита Михайлович, группа 11-201, 4 курс

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone <URL_РЕПОЗИТОРИЯ>
cd <ИМЯ_ПАПКИ>
```

### 2. Создать виртуальное окружение (рекомендуется)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Запустить краулер

```bash
python crawler.py
```

Краулер скачает все страницы из `urls_list.txt` и сохранит их в `pages/`.

---

## Структура проекта

```
project/
├── crawler.py          # Веб-краулер (Итерация 1)
├── requirements.txt    # Зависимости Python
├── urls_list.txt       # Список URL для скачивания
├── README.md           # Документация
├── SUBMISSION_CHECKLIST.md  # Чеклист для сдачи
├── pages/              # Скачанные HTML-страницы
│   ├── page_001.html
│   ├── page_002.html
│   └── ...
├── index.txt           # Индекс: номер файла -> URL
└── crawler.log         # Лог работы краулера
```

## Формат index.txt

```
1 https://ru.wikipedia.org/wiki/Информатика
2 https://ru.wikipedia.org/wiki/Алгоритм
3 https://ru.wikipedia.org/wiki/Программирование
...
```

## Повторный запуск

Краулер автоматически определяет уже скачанные страницы по `index.txt`
и пропускает их. Для полного перезапуска удалите `index.txt` и папку `pages/`.
