.globl solution
solution:
    mv a0, a1 # передвинул аргументы на нужное место,
    mv a1, a2 # потому что у gcc они в a0 и a1,
              # а по условию задания надо в a1, a2

    ble     a1,zero,.L1
    ld      a5,72(a0)
    ld      a2,56(a0)
    ld      a4,0(a0)
    li      a6,46
    or      a3,a5,a2
    or      a3,a3,a4
    addi    a4,a4,57
    ble     a3,a6,.L13
.L6:
    sd      a4,0(a0)
    li      a3,1
    addi    a4,a0,8
    li      a7,46
    beq     a1,a3,.L1
    ld      a6,0(a0)
    or      a5,a5,a2
    or      a5,a5,a6
    bgt     a5,a7,.L7
.L14:
    ld      a5,-8(a4)
    addi    a3,a3,1
    addi    a5,a5,-89
    sd      a5,0(a4)
    bge     a3,a1,.L1
.L11:
    ld      a5,72(a0)
    ld      a2,56(a0)
    ld      a6,0(a0)
    addi    a4,a4,8
    or      a5,a5,a2
    or      a5,a5,a6
    ble     a5,a7,.L14
.L7:
    ld      a5,0(a4)
    addi    a3,a3,1
    addi    a5,a5,57
    sd      a5,0(a4)
    bgt     a1,a3,.L11
.L1:
    ret
.L13:
    li      a4,-89
    j       .L6
    ret
