.globl solution
# run_flags: --time-scale=10
solution:
# a0 - number of led / button or read button state
# a1 - state of led

#s10 - conditions of buttons
#s11 - conditions of leds
#s8 = 8
#s9 - counter

    li s8, 8                # s8 <- 8
init:
    mv s9, zero
    mv s10, zero
    mv s11, zero            # s9, s10, s11 <- 0
loop_bt:
    mv a0, s9               # a0 <- button id
    call get_button_status  # a0 <- button status
    
    sll t0, a0, s9          # t0 = a0 << s9
    or s10, s10, t0         # s10 |= t0

    addi s9, s9, 1          # next button id
    blt s9, s8, loop_bt     # process next button

    srli t0, s10, 3
    andi t0, t0, 1
    srli t1, s10, 2
    andi t1, t1, 1
    srli t2, s10, 0
    andi t2, t2, 1
    xor s0, t1, t2
    or s0, t0, s0
    andi s0, s0, 1
    slli s0, s0, 0
    or s11, s11, s0

    srli t0, s10, 1
    andi t0, t0, 1
    srli t1, s10, 7
    andi t1, t1, 1
    and s0, t0, t1
    xori s0, s0, 1
    andi s0, s0, 1
    slli s0, s0, 1
    or s11, s11, s0

    srli t0, s10, 6
    andi t0, t0, 1
    srli t1, s10, 7
    andi t1, t1, 1
    srli t2, s10, 5
    andi t2, t2, 1
    or s0, t1, t2
    xor s0, t0, s0
    andi s0, s0, 1
    slli s0, s0, 2
    or s11, s11, s0

    srli t0, s10, 4
    andi t0, t0, 1
    srli t1, s10, 2
    andi t1, t1, 1
    and s0, t0, t1
    xori s0, s0, 1
    andi s0, s0, 1
    slli s0, s0, 3
    or s11, s11, s0

    srli t0, s10, 5
    andi t0, t0, 1
    srli t1, s10, 2
    andi t1, t1, 1
    and s0, t0, t1
    andi s0, s0, 1
    slli s0, s0, 4
    or s11, s11, s0

    srli t0, s10, 0
    andi t0, t0, 1
    srli t1, s10, 6
    andi t1, t1, 1
    or s0, t0, t1
    andi s0, s0, 1
    slli s0, s0, 5
    or s11, s11, s0

    srli t0, s10, 4
    xori t0, t0, 1
    srli t1, s10, 1
    andi t1, t1, 1
    srli t2, s10, 0
    xori t2, t2, 1
    xor s0, t1, t2
    or s0, t0, s0
    andi s0, s0, 1
    slli s0, s0, 6
    or s11, s11, s0

    srli t0, s10, 5
    andi t0, t0, 1
    srli t1, s10, 3
    andi t1, t1, 1
    srli t2, s10, 6
    andi t2, t2, 1
    and s0, t0, t1
    and s0, s0, t2
    andi s0, s0, 1
    slli s0, s0, 7
    or s11, s11, s0

    mv s9, zero
    mv t0, s11

loop_leds:
    mv a0, s9               # a0 <- s9
    andi a1, t0, 1          # a1 <- last bit of t0
    call set_led_status     # write LED status
    addi s9, s9, 1          # next LED id
    srli t0, t0, 1          # t0 >>= 1
    blt s9, s8, loop_leds   # next led

    call delay
    j init
