#!/bin/bash


# Integration test automation for interactive labs (2)
# Check incorrect and correct answer
# Collect general statistics and output

# ./tst/interactive_labs_integration_test.sh # check all tasks
# ./tst/interactive_labs_integration_test.sh lab2_debug  # check only given tasks



NO_COLOR='\033[0m'
BLUE_COLOR='\033[0;34m'
YELLOW_COLOR='\033[0;33m'
CYAN_COLOR='\033[0;36m'
RED_COLOR='\033[0;31m'
GREEN_COLOR='\033[0;32m'

if [ $# -eq 0 ] 
then
  echo "Task list is not set, checking all existing tasks"
  tasks="lab2_debug"
else
  tasks="$@"
  echo "Task list is:"
  echo ${tasks}
fi

fail_count=0

echo "Checking solutions for tasks"

task_counter=1
total_tasks=$(echo "$tasks" | wc -w)

seed_to_check="./tst/seed_to_check"
seeds=`cat ${seed_to_check}`

max_rand=100000
rand_count=100
rand_seeds=`shuf -i 1-${max_rand} -n ${rand_count}`

all_seeds=`echo ${seeds};echo ${rand_seeds}`


fail_solutions=`cat ./tst/interactive_lab_wrong_solutions | sed -e 's/$/;fail/'`

for task in ${tasks}
do
  echo -e "${YELLOW_COLOR}[${task_counter}/${total_tasks}] Starting check for ${task}:${NO_COLOR}"
  ((task_counter++))

  seed_counter=1
  total_seeds=$(echo "$all_seeds" | wc -w)

  for seed in ${all_seeds}
  do
    echo -e "\t${CYAN_COLOR}[${seed_counter}/${total_seeds}] Statring check ${task} seed=${seed}${NO_COLOR}"
    ((seed_counter++))
    success_solutions=`docker run --rm -it --entrypoint='' riscvcourse/workshop_risc-v bash -c 'python3 main.py lab2_debug -s '${seed}' --mode check  --jail-exec "" --jail-path "" > /dev/null || qemu-riscv64 ./prog.x 2>&1' | sed -e 's/$/;success/'`
    solutions=`echo ${success_solutions};echo ${fail_solutions}`

    solution_counter=1
    total_solutions=$(echo "$solutions" | wc -w)
   

    for s in ${solutions}
    do
      array=(${s//;/ })
      solution=${array[0]}
      expected_result=${array[1]}
      echo -e "\t\t${BLUE_COLOR}[${solution_counter}/${total_solutions}] Checking solution == ${solution}, expecting ${expected_result}${NO_COLOR}"
      ((solution_counter++))
      output=`docker run --rm -i riscvcourse/workshop_risc-v ${task} --mode check --seed ${seed} --answer ${solution}`
      exit_code="$?"

      echo "${output}"

      if [[ ("${expected_result}" == "success" && "${exit_code}" == "0" ) ||  ("${expected_result}" == "fail" && "${exit_code}" != "0" )  ]]
      then
        echo -e "\t\t${GREEN_COLOR}${task}, seed=${seed}, ${solution} is OK${NO_COLOR}"
      else
        let "fail_count++"
        echo -e "\t\t${RED_COLOR}Exit code does not match for ${task} seed=${seed} ${solution} - expected ${expected_result}, got exit_code=${exit_code}${NO_COLOR}"
      fi
      echo -e "\n"
    done 
  done

done

if [[ "${fail_count}" != "0" ]]
then
  echo "${RED_COLOR}Error, FAIL COUNT is ${fail_count}${NO_COLOR}"
  exit 1
else
  echo -e "${GREEN_COLOR}Everything is OK. Feel free to push${NO_COLOR}"
fi
