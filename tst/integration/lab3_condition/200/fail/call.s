.globl solution
.data
cmd:
    .string "echo Hello World!\0"
argv:
    .dword 0
.text
solution:
	la a0, cmd
    call system

    li a0, 0
    call exit
	ret
