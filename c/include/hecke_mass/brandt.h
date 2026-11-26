#ifndef HECKE_MASS_BRANDT_H
#define HECKE_MASS_BRANDT_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Count occurrences of target in a row of destination labels, including
 * repeated labels from distinct neighbors. A null row is valid when count
 * is zero. Otherwise destinations must point to at least count labels.
 */
size_t hecke_mass_brandt_count_u32(const uint32_t *destinations, size_t count,
                                   uint32_t target);

#ifdef __cplusplus
}
#endif

#endif
