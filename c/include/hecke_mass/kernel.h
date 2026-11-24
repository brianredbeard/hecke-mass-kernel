#ifndef HECKE_MASS_KERNEL_H
#define HECKE_MASS_KERNEL_H

#include <stddef.h>
#include <gmp.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Each function writes a reduced rational to an initialized GMP result.
 * Integer inputs must be nonnegative and rational inputs must be canonical.
 * A null input array is permitted when count is zero.
 */

/* Sum the reciprocals of the supplied orders. Zero orders contribute zero. */
void hecke_mass_class_mass(mpq_ptr result, const mpz_srcptr orders[], size_t count);

/* Sum samples and divide by u and q^(k * floor(rank/2)), with inv(0) = 0. */
void hecke_mass_hecke(mpq_ptr result, mpq_srcptr u, mpz_srcptr q, mpz_srcptr k,
                      mpz_srcptr rank, const mpq_srcptr samples[], size_t count);

#ifdef __cplusplus
}
#endif

#endif
