.globl solution

solution:
	add t0, a4, a2
	sub t0, a3, t0
	and t0, a4, t0
	sub t0, a2, t0
	add t0, a4, t0
	add t0, a3, t0
	add a0, a4, t0
	ret
