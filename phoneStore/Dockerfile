FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходные файлы приложения
COPY . /app/

# Открываем порт 8000 для Django
EXPOSE 8000

# Команда для запуска Django сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]