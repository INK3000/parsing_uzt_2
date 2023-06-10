#!/usr/bin/env sh

docker compose up --build --no-start
docker start parsing_uzt_2-api-1 parsing_uzt_2-nginx-1 parsing_uzt_2-telebot-1

