FROM python:3.9-slim

# Prevent Python from buffering logs (important for Cloud Run)
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app
WORKDIR $APP_HOME

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Cloud Run uses PORT env variable
ENV PORT=8080
EXPOSE 8080

# Use Gunicorn with dynamic PORT
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app