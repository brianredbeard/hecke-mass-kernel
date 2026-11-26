    .text
    .option push
    .option arch, +v

    .p2align 2
    .globl ime_vlenb
    .type ime_vlenb, @function
ime_vlenb:
    csrr a0, vlenb
    ret
    .size ime_vlenb, .-ime_vlenb

    .p2align 2
    .globl ime_multiply
    .type ime_multiply, @function
ime_multiply:
    vsetvli t0, zero, e32, m2, ta, ma
    vmv.v.i v16, 0
    vsetvli t0, zero, e8, m1, ta, ma
    vle8.v v4, (a0)
    vle8.v v5, (a1)
    # smt.vmadot v16, v4, v5, i8 (signed INT8 to INT32).
    .insn 0xe252382b
    vsetvli t0, zero, e32, m2, ta, ma
    vse32.v v16, (a2)
    ret
    .size ime_multiply, .-ime_multiply

    .option pop
    .section .note.GNU-stack,"",@progbits
