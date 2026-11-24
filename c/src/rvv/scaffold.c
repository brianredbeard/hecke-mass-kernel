#include <hecke_mass/scaffold.h>

#include <riscv_vector.h>

void hecke_mass_scaffold_probe(const uint32_t *input, uint32_t *output, size_t length)
{
    while (length != 0) {
        size_t active = __riscv_vsetvl_e32m1(length);
        vuint32m1_t words = __riscv_vle32_v_u32m1(input, active);
        vuint32m1_t result = __riscv_vxor_vx_u32m1(words, UINT32_C(0xa5a5a5a5), active);
        __riscv_vse32_v_u32m1(output, result, active);
        input += active;
        output += active;
        length -= active;
    }
}
