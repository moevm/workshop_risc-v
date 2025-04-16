.section .initial_jump


.global _start
.global asm_demo_func

.equ MTIME,      0x200BFF8    # Адрес mtime 
.equ MTIMECMP,   0x2004000    # Адрес mtimecmp
.equ SUCESS_FLAG, 0x1
.equ FAIL_FLAG,   0x0


.align 4
_start:
	la	sp, _sstack
	addi	sp,sp,-32
	sw	ra,28(sp)
	jal	ra, main


.section .data
.align 4
new_line:
	.ascii "\n"
	.byte 0


.section .text
.align 4
asm_demo_func:
    addi sp, sp, -32
    sw t0, 28(sp)
    sw a0, 24(sp)
	

    la t0, supervisor_trap_handler
    csrw stvec, t0          # Установка обработчика в stvec

    # Делегирование прерываний таймера в Supervisor mode (должно выполняться в Machine mode)
    # csrwi mideleg, 0x20    # Делегирование STIP (бит 5)
    # csrwi medeleg, 0x0     # Делегирование исключений (при необходимости)

    # Настройка таймера через SBI-вызов
    li a7, 0x54494D45       # SBI_EXT_ID_TIME
    li a6, 0x0              # SBI_FID_SET_TIMER
    li a0, 1000000          # Интервал в тиках
    ecall                   # Вызов SBI set_timer()

    # Включаем прерывания
    csrsi sstatus, 0x02     # Разрешаем прерывания (SIE)
    csrsi sie, 0x20         # Разрешаем прерывания таймера (STIE)

main_loop:
    wfi                     # Ожидание прерывания
    j main_loop

.align 4
supervisor_trap_handler:
    # Сохраняем контекст
    addi sp, sp, -32
    sw ra, 0(sp)
    sw t0, 4(sp)
    sw t1, 8(sp)
    sw a0, 12(sp)
    sw a7, 16(sp)

    # Проверяем причину прерывания
    csrr t0, scause
    li t1, 0x80000005       # Проверяем Supervisor Timer Interrupt
    bne t0, t1, not_timer

    # Обработка прерывания таймера
    li a7, 0x54494D45       # SBI_EXT_ID_TIME
    li a6, 0x0              # SBI_FID_SET_TIMER
    li a0, 1000000          # Новый интервал
    ecall                   # Установка нового таймера

    # Сбрасываем флаг прерывания
    csrci sip, 0x20         # Сброс STIP (бит 5)

not_timer:
    # Восстанавливаем контекст
    lw ra, 0(sp)
    lw t0, 4(sp)
    lw t1, 8(sp)
    lw a0, 12(sp)
    lw a7, 16(sp)

    addi sp, sp, 32
    lw t0, 28(sp)
    lw a0, 24(sp)
    addi sp, sp, 32
    ret
