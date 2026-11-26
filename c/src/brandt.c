#include <hecke_mass/brandt.h>

size_t hecke_mass_brandt_count_u32(const uint32_t *destinations, size_t count,
                                   uint32_t target)
{
    size_t hits = 0;
    for (size_t i = 0; i < count; ++i) {
        hits += destinations[i] == target;
    }
    return hits;
}
