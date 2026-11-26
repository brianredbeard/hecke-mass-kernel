#ifndef HECKE_MASS_F64_H
#define HECKE_MASS_F64_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Approximate a reciprocal sum in binary64. A zero order contributes zero
 * without division. Any uint32_t order converts exactly to binary64.
 * A null pointer is valid for an empty sum, which returns positive zero.
 * Otherwise orders must point to at least count entries.
 *
 * The scalar and ordered implementations round each reciprocal and add in
 * input order. The unordered RVV implementation can regroup additions within
 * a chunk and its result can depend on vector length. Without RVV, both
 * reduction variants use the scalar implementation.
 */
double hecke_mass_reciprocal_sum_scalar_f64(const uint32_t *orders, size_t count);
double hecke_mass_reciprocal_sum_ordered_f64(const uint32_t *orders, size_t count);
double hecke_mass_reciprocal_sum_unordered_f64(const uint32_t *orders, size_t count);

/*
 * Approximate the dot product of finite binary64 weights and samples. Each
 * product rounds before addition. The same reduction rules apply, and
 * intermediate products and sums follow binary64 overflow and underflow.
 * A null pointer is valid for either array when count is zero. Otherwise
 * each array must contain at least count entries.
 */
double hecke_mass_weighted_sum_scalar_f64(const double *weights,
                                          const double *samples, size_t count);
double hecke_mass_weighted_sum_ordered_f64(const double *weights,
                                           const double *samples, size_t count);
double hecke_mass_weighted_sum_unordered_f64(const double *weights,
                                             const double *samples, size_t count);

#ifdef __cplusplus
}
#endif

#endif
