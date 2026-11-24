#ifndef HECKE_MASS_SCAFFOLD_H
#define HECKE_MASS_SCAFFOLD_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Smoke test the library integration by XORing each input word with 0xa5a5a5a5.
 * Buffers must contain at least length words. They may be identical or disjoint.
 * When length is zero, both pointers may be null.
 */
void hecke_mass_scaffold_probe(const uint32_t *input, uint32_t *output, size_t length);

#ifdef __cplusplus
}
#endif

#endif
