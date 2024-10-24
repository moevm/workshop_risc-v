.globl solution
solution:
    # a0 -- arr1
    # a1 -- arr2
    # a2 -- arr3
    # a3 -- arr4
    # a4 -- len
    # a5 -- res
    # configure to use 32-bit elements
    vsetvli t0, a4, e32
    vle32.v v0, (a0)     # read batch of elements from arr1
    sub a4, a4, t0       # decrement by elements done
    slli t0, t0, 2       # no. elements to bytes offset
    add a0, a0, t0       # bump *arr1 pointer to next batch

    vle32.v v1, (a1)     # read batch of elements from arr2
    add a1, a1, t0       # bump *arr2 pointer to next batch

    vle32.v v2, (a2)     # read batch of elements from arr3
    add a2, a2, t0       # bump *arr3 pointer to next batch

    vle32.v v3, (a3)     # read batch of elements from arr3
    add a3, a3, t0       # bump *arr4 pointer to next batch

    vadd.vv v4, v0, v0
    vmul.vv v5, v3, v0
    vsub.vv v5, v2, v5
    vadd.vv v4, v4, v5
    vadd.vv v4, v1, v4
    vmul.vv v5, v3, v2
    vsub.vv v4, v5, v4
    vand.vv v4, v4, v3

    vse32.v v4, (a5)     # store result at *res

    add a5, a5, t0       # bump *zs pointer to next batch
    bgt a4, x0, solution        # is n = 0, or more elements left?

    ret
