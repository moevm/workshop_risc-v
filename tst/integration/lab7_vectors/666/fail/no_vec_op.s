.globl solution
solution:
    # при старте данной метки ваша программа должна выполнить 
    # поэлементные векторные вычисления по заданной формуле
    vsetvli t0, a4, e32
    vle32.v v0, (a0)
    vse32.v v0, (a5)
    ret