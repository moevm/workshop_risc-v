#!/bin/bash


operation=${1}
task=${2}
seed=${3}

# TODO - check Docker connection
# TODO - check task for existance

if [ "$#" -ne 3 ]
then
  cat << EndOfMessage
  Usage
  ./scripts/shell.sh operation task seed
   - operation = {init, check}
   - task - task_id from ./tasks/
   - seed - random seed to pass
EndOfMessage

  exit 1
fi 

if [[ "${operation}" == "init"  ]];
then
  ./scripts/init_task.sh ${task} ${seed}
elif [[ "${operation}" == "check"   ]];
then
  ./scripts/check_task.sh ${task} ${seed}
else
  echo "Unknown operation ${operation}, terminating"
  exit 1
fi
