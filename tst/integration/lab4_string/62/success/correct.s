.globl main
.text
.LCPI0_0:
        .quad   2635249153387078803
.LCPI0_1:
        .quad   5270498306774157605
.LCPI0_2:
        .quad   -3689348814741910323
solve:
.Lpcrel_hi0:
        auipc   a0, %pcrel_hi(str)
        addi    t1, a0, %pcrel_lo(.Lpcrel_hi0)
        lbu     a4, 0(t1)
        beqz    a4, .LBB0_9
.Lpcrel_hi1:
        auipc   a1, %pcrel_hi(.LCPI0_0)
        ld      a6, %pcrel_lo(.Lpcrel_hi1)(a1)
        addi    a2, t1, 1
        li      a3, 9
.LBB0_2:
        addi    a5, a4, -48
        bltu    a3, a5, .LBB0_4
        andi    a4, a4, 15
        mulhu   a5, a4, a6
        slli    a1, a5, 3
        add     a4, a4, a5
        sub     a4, a4, a1
        addi    a1, a4, 48
        sb      a1, -1(a2)
.LBB0_4:
        lbu     a4, 0(a2)
        addi    a2, a2, 1
        bnez    a4, .LBB0_2
        lbu     t2, 0(t1)
        beqz    t2, .LBB0_10
        li      a2, 0
        addi    a3, t1, 1
        mv      a4, t2
.LBB0_7:
        andi    a5, a4, 255
        lbu     a4, 0(a3)
        addi    a5, a5, -95
        seqz    a5, a5
        add     a2, a2, a5
        addi    a3, a3, 1
        bnez    a4, .LBB0_7
.Lpcrel_hi2:
        auipc   a3, %pcrel_hi(.LCPI0_1)
        ld      a3, %pcrel_lo(.Lpcrel_hi2)(a3)
        sltiu   a4, a2, 7
        srli    a5, a2, 1
        mulhu   a3, a5, a3
        li      a5, -5
        srli    a5, a5, 2
        and     a5, a5, a3
        slli    a3, a3, 3
        andi    a3, a3, -16
        sub     a3, a3, a5
        addi    a4, a4, -1
        and     a3, a3, a4
        sub     a2, a2, a3
        j       .LBB0_11
.LBB0_9:
        li      t2, 0
.LBB0_10:
        li      a2, 0
.LBB0_11:
        li      a0, 0
.Lpcrel_hi3:
        auipc   a3, %pcrel_hi(tmp)
.Lpcrel_hi4:
        auipc   a5, %pcrel_hi(.LCPI0_2)
        ld      a6, %pcrel_lo(.Lpcrel_hi4)(a5)
        addi    a3, a3, %pcrel_lo(.Lpcrel_hi3)
        li      a7, 10
        li      t0, 9
.LBB0_12:
        mv      a4, a2
        add     a5, a3, a0
        mulhu   a2, a2, a6
        srli    a2, a2, 3
        mul     a1, a2, a7
        subw    a1, a4, a1
        ori     a1, a1, 48
        sb      a1, 0(a5)
        addi    a0, a0, 1
        bltu    t0, a4, .LBB0_12
        srli    a6, a0, 1
        beqz    a6, .LBB0_16
        add     a4, a3, a0
        addi    a4, a4, -1
        seqz    a1, a6
        add     a1, a1, a6
        sub     a5, a5, a1
.LBB0_15:
        lbu     a1, 0(a4)
        lbu     a2, 0(a3)
        sb      a1, 0(a3)
        sb      a2, 0(a4)
        addi    a4, a4, -1
        addi    a3, a3, 1
        bne     a4, a5, .LBB0_15
.LBB0_16:
.Lpcrel_hi5:
        auipc   a1, %pcrel_hi(str2)
        addi    a4, a1, %pcrel_lo(.Lpcrel_hi5)
        li      a6, 32
.Lpcrel_hi6:
        auipc   a1, %pcrel_hi(tmp)
        addi    a7, a1, %pcrel_lo(.Lpcrel_hi6)
.LBB0_17:
        andi    a3, t2, 255
        beq     a3, a6, .LBB0_20
        beqz    a3, .LBB0_24
        sb      t2, 0(a4)
        li      a3, 1
        j       .LBB0_23
.LBB0_20:
        mv      a1, a7
        mv      a3, a4
.LBB0_21:
        lbu     a2, 0(a1)
        addi    a1, a1, 1
        addi    a5, a3, 1
        sb      a2, 0(a3)
        mv      a3, a5
        bnez    a2, .LBB0_21
        mv      a3, a0
.LBB0_23:
        lbu     t2, 1(t1)
        addi    t1, t1, 1
        add     a4, a4, a3
        j       .LBB0_17
.LBB0_24:
.Lpcrel_hi7:
        auipc   a0, %pcrel_hi(str2)
        addi    a0, a0, %pcrel_lo(.Lpcrel_hi7)
        lbu     a2, 0(a0)
        beqz    a2, .LBB0_31
.Lpcrel_hi8:
        auipc   a1, %pcrel_hi(lowercase)
        addi    a6, a1, %pcrel_lo(.Lpcrel_hi8)
.Lpcrel_hi9:
        auipc   a1, %pcrel_hi(uppercase)
        addi    a7, a1, %pcrel_lo(.Lpcrel_hi9)
.LBB0_26:
        li      a4, 20
        mv      a5, a7
        mv      a1, a6
.LBB0_27:
        lbu     a3, 0(a5)
        beq     a2, a3, .LBB0_29
        addi    a1, a1, 1
        addi    a4, a4, -1
        addi    a5, a5, 1
        bnez    a4, .LBB0_27
        j       .LBB0_30
.LBB0_29:
        lbu     a1, 0(a1)
        sb      a1, 0(a0)
.LBB0_30:
        lbu     a2, 1(a0)
        addi    a0, a0, 1
        bnez    a2, .LBB0_26
.LBB0_31:
.Lpcrel_hi10:
        auipc   a0, %pcrel_hi(str)
        addi    a0, a0, %pcrel_lo(.Lpcrel_hi10)
.Lpcrel_hi11:
        auipc   a1, %pcrel_hi(str2)
        addi    a1, a1, %pcrel_lo(.Lpcrel_hi11)
.LBB0_32:
        lbu     a2, 0(a1)
        addi    a1, a1, 1
        addi    a3, a0, 1
        sb      a2, 0(a0)
        mv      a0, a3
        bnez    a2, .LBB0_32
        ret

main:
        li a0, 0
        la a1, str
        li a2, 255
        li a7, 63
        ecall

        call solve

        li t0, 0
        la t1, str
        j cond
loop:
        addi t0, t0, 1
        addi t1, t1, 1
cond:
        lb t2, 0(t1)
        bne t2, zero, loop

        li a0, 1
        la a1, str
        mv a2, t0
        li a7, 64
        ecall

        li a0, 0
        li a7, 93
        ecall
    
.data
str:
        .zero 256
str2:
        .zero 256
tmp:
        .zero 16
lowercase:
        .string "bcdfghjklmnpqrstvwxz"
uppercase:
        .string "BCDFGHJKLMNPQRSTVWXZ"
