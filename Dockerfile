FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ARG APP_VERSION=dev
ARG GIT_COMMIT=unknown
ENV APP_VERSION=$APP_VERSION \
    GIT_COMMIT=$GIT_COMMIT

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
