FROM python:3.13-slim
WORKDIR /usr/local/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY utils.py .

COPY /frontend ./frontend/

EXPOSE 8080
CMD ["uvicorn", "main:app","--host","0.0.0.0","--port","8080"]