#include <hecke_mass/scaffold.h>

int main(void)
{
    const uint32_t input = 0;
    uint32_t output;

    hecke_mass_scaffold_probe(&input, &output, 1);
    return output == UINT32_C(0xa5a5a5a5) ? 0 : 1;
}
