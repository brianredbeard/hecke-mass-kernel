#include <hecke_mass/brandt.h>

#include <riscv_vector.h>

size_t hecke_mass_brandt_count_u32(const uint32_t *destinations, size_t count,
                                   uint32_t target)
{
    size_t hits = 0;
    while (count != 0) {
        const size_t active = __riscv_vsetvl_e32m8(count);
        vuint32m8_t labels = __riscv_vle32_v_u32m8(destinations, active);
        vbool4_t matches = __riscv_vmseq_vx_u32m8_b4(labels, target, active);
        hits += __riscv_vcpop_m_b4(matches, active);
        destinations += active;
        count -= active;
    }
    return hits;
}
