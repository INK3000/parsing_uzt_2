FROM python:3.11-alpine

WORKDIR /app

RUN pip install pip --upgrade 
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD [ "uvicorn", "parsing_uzt_2.asgi:application", "--host", "0.0.0.0", "--port", "8000"  ]
