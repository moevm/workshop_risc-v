#!/bin/bash

# This script checks a0 values (correct answer for lab2) for range of seeds
# The goal is to check that some values are not more frequent than others in order to finetune this lab

end_val=${1:-20}
start_val=${2:-1}

for i in $(seq $start_val $end_val); 
do 
  res=`docker run --rm -it --entrypoint='' riscvcourse/workshop_risc-v bash -c 'python3 main.py lab2_debug -s '$i' --mode check > /dev/null || qemu-riscv64 ./prog.x 2>&1';`
  echo ${res}
done
