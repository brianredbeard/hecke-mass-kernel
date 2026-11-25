#include <hecke_mass/kernel.h>

int main(void)
{
    mpz_t four, six, q, k, rank;
    mpq_t result, u, first, second;
    mpz_init_set_ui(four, 4);
    mpz_init_set_ui(six, 6);
    mpz_init_set_ui(q, 3);
    mpz_init_set_ui(k, 1);
    mpz_init_set_ui(rank, 3);
    mpq_inits(result, u, first, second, NULL);
    mpq_set_si(u, -1, 1);
    mpq_set_si(first, 2, 1);
    mpq_set_si(second, 4, 1);

    const mpz_srcptr orders[] = {four, six};
    int mass_ok = hecke_mass_class_mass_checked(result, orders, 2) == HECKE_MASS_OK &&
                  mpq_cmp_ui(result, 5, 12) == 0;

    const mpq_srcptr samples[] = {first, second};
    int hecke_ok = hecke_mass_hecke_checked(result, u, q, k, rank, samples, 2) == HECKE_MASS_OK &&
                   mpq_cmp_si(result, -2, 1) == 0;

    mpq_clears(result, u, first, second, NULL);
    mpz_clears(four, six, q, k, rank, NULL);
    return mass_ok && hecke_ok ? 0 : 1;
}
