.text
on_event:
    j on_event

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
    la a4, on_event        # set function pointer
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
