#include <hecke_mass/f64.h>

#include <riscv_vector.h>
#include <stdbool.h>

static vfloat64m1_t reduce(vfloat64m8_t terms, vfloat64m1_t sum, size_t active,
                           bool ordered)
{
    if (ordered) {
        return __riscv_vfredosum_vs_f64m8_f64m1(terms, sum, active);
    }
    return __riscv_vfredusum_vs_f64m8_f64m1(terms, sum, active);
}

static double reciprocal_sum(const uint32_t *orders, size_t count, bool ordered)
{
    vfloat64m1_t sum = __riscv_vfmv_s_f_f64m1(0.0, 1);
    while (count != 0) {
        /* e32,m4 and e64,m8 have the same lane capacity. */
        const size_t active = __riscv_vsetvl_e32m4(count);
        const vuint32m4_t values = __riscv_vle32_v_u32m4(orders, active);
        const vbool8_t nonzero = __riscv_vmsne_vx_u32m4_b8(values, 0, active);
        const vfloat64m8_t denominators = __riscv_vfwcvt_f_xu_v_f64m8(values, active);
        const vfloat64m8_t zeros = __riscv_vfmv_v_f_f64m8(0.0, active);
        const vfloat64m8_t terms =
            __riscv_vfrdiv_vf_f64m8_mu(nonzero, zeros, denominators, 1.0, active);
        sum = reduce(terms, sum, active, ordered);
        orders += active;
        count -= active;
    }
    return __riscv_vfmv_f_s_f64m1_f64(sum);
}

static double weighted_sum(const double *weights, const double *samples, size_t count,
                           bool ordered)
{
    vfloat64m1_t sum = __riscv_vfmv_s_f_f64m1(0.0, 1);
    while (count != 0) {
        const size_t active = __riscv_vsetvl_e64m8(count);
        const vfloat64m8_t left = __riscv_vle64_v_f64m8(weights, active);
        const vfloat64m8_t right = __riscv_vle64_v_f64m8(samples, active);
        const vfloat64m8_t terms = __riscv_vfmul_vv_f64m8(left, right, active);
        sum = reduce(terms, sum, active, ordered);
        weights += active;
        samples += active;
        count -= active;
    }
    return __riscv_vfmv_f_s_f64m1_f64(sum);
}

double hecke_mass_reciprocal_sum_ordered_f64(const uint32_t *orders, size_t count)
{
    return reciprocal_sum(orders, count, true);
}

double hecke_mass_reciprocal_sum_unordered_f64(const uint32_t *orders, size_t count)
{
    return reciprocal_sum(orders, count, false);
}

double hecke_mass_weighted_sum_ordered_f64(const double *weights,
                                           const double *samples, size_t count)
{
    return weighted_sum(weights, samples, count, true);
}

double hecke_mass_weighted_sum_unordered_f64(const double *weights,
                                             const double *samples, size_t count)
{
    return weighted_sum(weights, samples, count, false);
}
