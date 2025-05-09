# 🖨️ Django Print Event Tracker

Django-приложение для импорта, анализа и визуализации журналов печати.  
Поддерживает CSV и JSON импорты, фильтрацию по подразделениям и экспорт в Excel.

## 🚀 Возможности

- Импорт пользователей из CSV-файла (OU, SamAccountName, ФИО)
- Импорт событий печати из JSON-лога
- Фильтрация событий по подразделениям и датам
- Иерархическое отображение событий (отдел → принтер → пользователь → документ)
- Экспорт в Excel (.xlsx)
- Интеграция с PostgreSQL
- Готово для продакшн-деплоя в Docker

---

## 🛠️ Установка

### 1. Клонируйте проект и создайте окружение

```bash
git clone https://your.repo/print-advisor.git
cd print-advisor
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
```

### 2. Настройте подключение к PostgreSQL

В `advisor_django/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'your_host',
        'PORT': '5432',
    }
}
```

---

### 3. Миграции и суперпользователь

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

---

### 4. Запуск сервера

```bash
python manage.py runserver
```

Открой `/http://127.0.0.1:8000/` в браузере  
Админка: `/http://127.0.0.1:8000/admin/`

---

## 📂 Структура проекта

```txt
advisor_django/
├── advisor_django/        # Настройки Django
├── core/                  # Приложение обработки печати
│   ├── models/            # ORM-модели
│   ├── views/             # Вьюхи
│   ├── templates/core/    # Шаблоны
│   ├── services/          # Импортеры CSV/JSON
│   └── urls.py
├── templates/             # Расширяемые шаблоны
├── manage.py
└── requirements.txt
```

---

## 📥 Импорт пользователей (CSV)

- URL: `/upload/`
- Поддерживаемые поля: `/SamAccountName/`, `/DisplayName/`, `/OU/`
- Альтернатива: POST `/import/users/`

## 📥 Импорт событий печати (JSON)

- URL: `/upload/`
- JSON должен быть списком событий формата: `/Param1/`, `/Param2/`, ..., `/TimeCreated/`, `/JobID/`, ...

## 📤 Экспорт в Excel

- Страница: `/print-tree/`
- Кнопка `/📥 Выгрузить в Excel/`

---

## 🐳 Docker

Проект совместим с Docker. В логах:
- все события логируются через `logging` в stdout/stderr
- поддерживается CI/CD-friendly деплой

---

## 🧠 Автор

Создан с AI  
Поддержка и доработка — пишите на `/RoKols2017@gmail.com/` 

