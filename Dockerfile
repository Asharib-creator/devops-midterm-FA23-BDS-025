# Runtime image for the FastAPI model service (FA23-BDS-025)
FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
# requirements.lock is written by Jenkins (pip freeze of the training venv),
# so the container uses exactly the library versions the model was trained with.
COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock
COPY app.py config.json ./
COPY artifacts/ ./artifacts/
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
