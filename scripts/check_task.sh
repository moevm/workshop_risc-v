#!/bin/bash

set -e

task=${1}
seed=${2}


echo "Проверка задания ${task} с seed=${seed}"


cd ./src/tasks/${task}

if ./check.sh ${seed}
then
  echo "Проверка прошла успешно."

  # If NO_TOKEN env var is set - do not generate and output token
  if [ -z ${NO_TOKEN+x} ];
  then
    echo "Ваш проверочный token будет выведен ниже:"
    python3 ../../token/generate.py "${task}_${seed}"
  fi

else
  echo "При проверке решения возникли ошибки"
  exit 1
fi
