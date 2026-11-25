#ifndef HECKE_MASS_KERNEL_H
#define HECKE_MASS_KERNEL_H

#include <stddef.h>
#include <gmp.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum hecke_mass_status {
    HECKE_MASS_OK = 0,
    HECKE_MASS_ERR_INVALID_ARGUMENT = 1
} hecke_mass_status;

/*
 * Each function writes a reduced rational to an initialized GMP result.
 * Integer inputs must be nonnegative and rational inputs must be canonical
 * with positive denominators. A null input array is permitted when count is
 * zero. Output aliasing (for example, result == u or result == samples[i])
 * is supported.
 *
 * The `_checked` variants validate pointers, integer signs, and positive
 * denominators and return HECKE_MASS_ERR_INVALID_ARGUMENT without modifying
 * result when validation fails. The void variants delegate to the checked
 * implementations and set result to 0 if an invalid input is supplied.
 */

/* Sum the reciprocals of the supplied orders. Zero orders contribute zero. */
hecke_mass_status hecke_mass_class_mass_checked(mpq_ptr result,
                                                const mpz_srcptr orders[],
                                                size_t count);

void hecke_mass_class_mass(mpq_ptr result, const mpz_srcptr orders[], size_t count);

/* Sum samples and divide by u and q^(k * floor(rank/2)), with inv(0) = 0. */
hecke_mass_status hecke_mass_hecke_checked(mpq_ptr result, mpq_srcptr u,
                                           mpz_srcptr q, mpz_srcptr k,
                                           mpz_srcptr rank,
                                           const mpq_srcptr samples[],
                                           size_t count);

void hecke_mass_hecke(mpq_ptr result, mpq_srcptr u, mpz_srcptr q, mpz_srcptr k,
                      mpz_srcptr rank, const mpq_srcptr samples[], size_t count);

#ifdef __cplusplus
}
#endif

#endif
