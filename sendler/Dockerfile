FROM python:3.11-alpine

WORKDIR /app

RUN pip install pip --upgrade
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY /sendler ./sendler

CMD [ "python", "-m", "sendler"]
