.globl main
.text
main:
    li a0, 1
    la a1, message
    li a2, 13
    li a7, 64
    ecall
    
    li a0, 0
    li a7, 93
    ecall

.data
message: .string "sample string"
