#!/bin/bash

# Generar el archivo .env con las variables de entorno
echo "SECRET=\"$SECRET\"" > .env
echo "APP_ENV='$APP_ENV'" >> .env
echo "BILLPG_DB='$BILLPG_DB'" >> .env
echo "BILLPG_HOST='$BILLPG_HOST'" >> .env
echo "BILLPG_PASSWORD='$ODINPG_USER'" >> .env
echo "BILLPG_PORT='$ODINPG_USER'" >> .env
echo "BILLPG_USER='$ODINPG_USER'" >> .env
echo "BILLPG_SCHEMA='$ODINPG_USER'" >> .env
echo "BILLORA_DB='$BILLORA_DB'" >> .env
echo "BILLORA_HOST='$BILLORA_HOST'" >> .env
echo "BILLORA_PASSWORD='$BILLORA_PASSWORD'" >> .env
echo "BILLORA_PORT='$BILLORA_PORT'" >> .env
echo "BILLORA_USER='$BILLORA_USER'" >> .env
echo "BILLORA_SCHEMA='$BILLORA_SCHEMA'" >> .env
echo "TITANIO_HOST='$TITANIO_HOST'" >> .env
echo "TITANIO_NIT='$TITANIO_NIT'" >> .env
echo "TITANIO_USER='$TITANIO_USER'" >> .env
echo "TITANIO_PWD='$TITANIO_PWD'" >> .env








# Ejecutar el comando CMD del Dockerfile
exec "$@"