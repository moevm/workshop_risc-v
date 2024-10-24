#!/bin/bash


# Integration test automation for default (non interactive) labs (1, 3-7), where
# For each lab use ideal solutions from tst/integration/<lab_name>/<seed>/<exprected_result>/<reason_name.s> does check result matches with exprected_result
# Collect general statistics and output

# ./tst/default_labs_integration_test.sh # check all tasks, that have solutions at tst/integration/<lab_name>/
# ./tst/default_labs_integration_test.sh lab3_condition  # check only given tasks


# TODO
# args 
# collect fails in one list

NO_COLOR='\033[0m'
BLUE_COLOR='\033[0;34m'
YELLOW_COLOR='\033[0;33m'
CYAN_COLOR='\033[0;36m'
RED_COLOR='\033[0;31m'
GREEN_COLOR='\033[0;32m'

tasks_dir="./tst/integration/"
if [ $# -eq 0 ] 
then
  echo "Task list is not set, checking all existing tasks"
  tasks=`ls -1 ${tasks_dir} | grep '^lab'`
  checker_run_flags=''
else
  while [[ $# -gt 0 ]]; do
    case $1 in
      -f)
        checker_run_flags+=" $2"
        shift
        shift
        ;;
      -*|--*)
        echo "Unknown option $1"
        exit 1
        ;;
      *)
        tasks+=" $1"
        shift
        ;;
    esac
  done
  echo "Task list is:"
  echo "${tasks}"
  echo "Checker run flags are:"
  echo "${checker_run_flags}"
fi

fail_count=0

echo "Checking solutions for tasks"

task_counter=1
total_tasks=$(echo "$tasks" | wc -w)

for task in ${tasks}
do
  echo -e "${YELLOW_COLOR}[${task_counter}/${total_tasks}] Starting check for ${task}:${NO_COLOR}"
  ((task_counter++))
  seeds=`ls -1 ${tasks_dir}/${task}/`

  seed_counter=1
  total_seeds=$(echo "$seeds" | wc -w)

  for seed in ${seeds}
  do
    echo -e "\t${CYAN_COLOR}[${seed_counter}/${total_seeds}] Statring check ${task} seed=${seed}${NO_COLOR}"
    ((seed_counter++))
    
    if ! ( [ -d ${tasks_dir}/${task}/${seed}/success/ ] && [ -d ${tasks_dir}/${task}/${seed}/fail/ ] ) ; then
      echo -e "\t\tError - some testing solutions are not present for ${task} seed=${seed}  (look below - fail and success dirs should exist):"
      ls -la ${tasks_dir}/${task}/${seed}/
      let "fail_count++"
      continue
    fi
    
    success_solutions=`ls -1 ${tasks_dir}/${task}/${seed}/success/ | sed -e 's/$/;success/'`
    fail_solutions=`ls -1 ${tasks_dir}/${task}/${seed}/fail/ | sed -e 's/$/;fail/'`
    solutions=`echo ${success_solutions};echo ${fail_solutions}`

    solution_counter=1
    total_solutions=$(echo "$solutions" | wc -w)

    for s in ${solutions}
    do
      array=(${s//;/ })
      solution=${array[0]}
      expected_result=${array[1]}
      solution_path="$(pwd)/${tasks_dir}/${task}/${seed}/${expected_result}/${solution}"
      echo -e "\t\t${BLUE_COLOR}[${solution_counter}/${total_solutions}] Checking ${solution} (${solution_path}), expecting ${expected_result}${NO_COLOR}"
      ((solution_counter++))

      current_checker_run_flags=`echo ${checker_run_flags}; cat ${solution_path} | grep -Po '(?<=run_flags:).*'`
      output=`docker run --rm -t -v ${solution_path}:/app/solution.s:ro riscvcourse/workshop_risc-v ${task} --mode=check --seed=${seed} $current_checker_run_flags`
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
  echo -e "${RED_COLOR}Error, FAIL COUNT is ${fail_count}${NO_COLOR}"
  exit 1
else
  echo -e "${GREEN_COLOR}Everything is OK. Feel free to push${NO_COLOR}"
fi
