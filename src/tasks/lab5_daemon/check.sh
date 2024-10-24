#!/bin/bash

set -e

filename="/app/solution.s"

# Check file exist

if [[ ! -f ${filename} ]]
then
  echo "Ошибка: Файл решения не найден."
  exit 1
fi

cp ${filename} .

X=${PARAM_X:-3}

if [ "$INTERACTIVE" == "1" ]
then
    python3 check.py --seed ${1} --interactive -x ${X}
else
    python3 check.py --seed ${1} -x ${X}
fi
