#!/bin/bash

set -e

task=${1}
seed=${2}

echo "Инициализация задания ${task} с seed=${seed}"

cd ./src/tasks/${task}/

cat ./description.md

./init.sh ${seed}
