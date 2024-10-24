.text
on_event:
    # updating counter
    la a0, listener_table
    li a1, 10
    la a2, n
    lw a2, 0(a2)
    mul a1, a2, a1
    add a1, a1, a0
    lh a2, 8(a1)
    addi a2, a2, 1
    sh a2, 8(a1) 
    
    # calculating a & (b | c)
    la a0, a
    la a1, b
    la a2, c
    ld a0, 0(a0)
    ld a1, 0(a1)
    ld a2, 0(a2)
    
    or a1, a1, a2
    and a0, a0, a1

    ret

load:
    la a6, n                # increment listener_table.n + store in to local "n"
    la a5, listener_table
    lw a4, 6(a5)
    addiw a4, a4, 1
    sw a4, 0(a6)
    sw a4, 6(a5)

    li a6, 10                # a5 = listener_table.data[n]
    mul a4, a4, a6 
    add a5, a5, a4
    li a4, 123123123      # set function pointer
    sd a4, 0(a5)
    sh zero, 8(a5)         # set counter to 0
    ret

unload:
    la a5, listener_table # decrement listener_table.n
    lw a4, 6(a5)
    addiw a4, a4, -1
    sw a4, 6(a5)
    ret

.data
n:
    .zero   4

.globl load
.globl unload
