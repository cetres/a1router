#!/bin/sh
if [ -z "$VIRTUAL_ENV" ]; then
  echo "Ambiente virtual nao ativado"
  if [ ! -d "env" ]; then
    echo "Ambiente virtual nao configurado"
    virtualenv env
  fi
  source env/bin/activate
  echo "Ambiente virtual ativado"
fi

pip install -r requirements.txt
