#!/bin/bash

# Run generation for each lab on big number of seeds, check for non zero exit codes

# ./tst/seed_stress_test.sh # check all tasks
# ./tst/seed_stress_test.sh lab2_debug lab3_condition # check only specified tasks

# Docker SHOULD BE ALREADY BUILD before you run this script

# TODO
# args support 
# -- check random seeds only (--num)
# -- check only from ./seed_to_check



tasks_dir="./src/riscv_course/"

if [ $# -eq 0 ] 
then
  echo "Task list is not set, checking all existing tasks"
  tasks=`ls -1 ${tasks_dir} | grep '^lab'`
else
  tasks="$@"
  echo "Task list is:"
  echo ${tasks}
fi

seed_to_check="./tst/seed_to_check"
seeds=`cat ${seed_to_check}`

max_rand=100000
rand_count=100
rand_seeds=`shuf -i 1-${max_rand} -n ${rand_count}`

all_seeds=`echo ${seeds};echo ${rand_seeds}`

fail_count=0

seed_counter=1
total_seeds=$(echo "$all_seeds" | wc -w)

task_counter=1
total_tasks=$(echo "$tasks" | wc -w)

for task in ${tasks}
do 
  echo "[${task_counter}/${total_tasks}] Starting check for ${task}:"
  ((task_counter++))
  for seed in ${all_seeds}
  do
    echo "[${seed_counter}/${total_seeds}] Checking ${task} seed=${seed}"
    ((seed_counter++))
    output=`docker run -e NO_TOKEN=true --rm -it  riscvcourse/workshop_risc-v ${task} --mode init --seed ${seed}`
    if [[ "$?" == "0" ]]
    then 
      if [[ "${output}" == "" ]] || [[ "${output}" == *"None"* ]]
      then    
        let "fail_count++"
        echo "Empty or 'None' output for ${task} seed=${seed}"
      else
        echo "${task} seed=${seed} is OK"
      fi

    else
      let "fail_count++"
      echo "Non zero exit code for ${task} seed=${seed}, output is below:"
      echo ${output}
    fi 
  done
  seed_counter=1
done

if [[ "${fail_count}" != "0" ]]
then
  echo "Error, FAIL COUNT is ${fail_count}"
  exit 1
else
  echo "All seeds are OK"
fi
