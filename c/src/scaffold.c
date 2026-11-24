#include <hecke_mass/scaffold.h>

void hecke_mass_scaffold_probe(const uint32_t *input, uint32_t *output, size_t length)
{
    for (size_t index = 0; index < length; ++index) {
        output[index] = input[index] ^ UINT32_C(0xa5a5a5a5);
    }
}
