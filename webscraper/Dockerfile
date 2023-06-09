FROM python:3.11-alpine
ENV PYTHONUNBUFFERED 1
WORKDIR /app 

RUN pip install pip --upgrade
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . ./webscraper

CMD [ "python", "-m", "webscraper"  ]
