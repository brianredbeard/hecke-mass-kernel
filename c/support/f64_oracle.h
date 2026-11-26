#ifndef HECKE_MASS_F64_ORACLE_H
#define HECKE_MASS_F64_ORACLE_H

#include <gmp.h>
#include <stddef.h>
#include <stdint.h>

/*
 * Round a canonical rational to IEEE 754 binary64, nearest with ties to even.
 * Overflow returns signed infinity. A nonzero value rounding to zero retains
 * its sign. Exact zero returns positive zero.
 */
double hecke_mass_binary64_round(mpq_srcptr value);

/*
 * Both sums return 1 on success or 0 on invalid input or buffer allocation failure.
 * The output must be initialized and is only modified on success.
 * A null input array is allowed when count is zero.
 * Zero orders contribute zero to the reciprocal sum.
 * The weighted sum interprets finite binary64 inputs exactly.
 */
int hecke_mass_exact_reciprocal_sum(mpq_ptr out, const uint32_t *orders, size_t count);
int hecke_mass_exact_weighted_sum(mpq_ptr out, const double *weights,
                                 const double *samples, size_t count);

#endif
