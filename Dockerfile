FROM python:3.11-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


RUN adduser --disabled-password --gecos "" app_user


WORKDIR /app


COPY app/requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY app/ .


RUN chown -R app_user:app_user /app


USER app_user


EXPOSE 8080
EXPOSE 9999

CMD ["python", "app.py"]