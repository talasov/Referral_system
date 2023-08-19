# Используйте базовый образ Python
FROM python:3.9

# Установите переменную окружения для запуска в режиме production
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Установите рабочую директорию в /app
WORKDIR /app

# Скопируйте зависимости и файлы проекта в контейнер
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/

# Соберите статические файлы
RUN python manage.py collectstatic --noinput

# Запустите проект на порту 8000
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
