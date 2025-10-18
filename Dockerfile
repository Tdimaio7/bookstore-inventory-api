FROM python:3.11-slim

WORKDIR /app

COPY requeriments.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ejecuta migraciones y levanta el servidor
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]

