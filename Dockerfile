FROM python:latest

WORKDIR /app
COPY . /app

RUN mkdir -p ./fig
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./main.py"]