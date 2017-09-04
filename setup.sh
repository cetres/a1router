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

exportLDFLAGS=-L/usr/local/opt/qt/lib
export CPPFLAGS=-I/usr/local/opt/qt/include

pip install -r requirements.txt
