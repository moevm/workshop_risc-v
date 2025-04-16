    .section .text
    .globl _start

_start:
    la t0, interrupt_handler
    csrw mtvec, t0

    li t1, 0x800
    csrs mstatus, t1

    li t2, 0x80000000 
    csrw mie, t2

    # Бесконечный цикл для ожидания прерывания
1:
    j 1b

interrupt_handler:
    # Выводим сообщение
    li a0, 1
    la a1, msg
    li a2, 14
    li a7, 64
    ecall

    # Завершаем программу
    li a7, 93
    li a0, 0
    ecall

    .section .data
msg:
    .asciz "Interrupt!\n"
