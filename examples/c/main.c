#include <hecke_mass/kernel.h>

int main(void)
{
    mpz_t four, six, q, k, rank, group;
    mpq_t result, u, first, second, covered, expected_total;
    mpz_init_set_ui(four, 4);
    mpz_init_set_ui(six, 6);
    mpz_init_set_ui(q, 3);
    mpz_init_set_ui(k, 1);
    mpz_init_set_ui(rank, 3);
    mpz_init_set_ui(group, 24);
    mpq_inits(result, u, first, second, covered, expected_total, NULL);
    mpq_set_si(u, -1, 1);
    mpq_set_si(first, 2, 1);
    mpq_set_si(second, 4, 1);

    const mpz_srcptr orders[] = {four, six};
    int mass_ok = hecke_mass_class_mass_checked(result, orders, 2) == HECKE_MASS_OK &&
                  mpq_cmp_ui(result, 5, 12) == 0;

    const mpq_srcptr samples[] = {first, second};
    int hecke_ok = hecke_mass_hecke_checked(result, u, q, k, rank, samples, 2) == HECKE_MASS_OK &&
                   mpq_cmp_si(result, -2, 1) == 0;

    mpq_set_ui(expected_total, 11, 1);
    int orbit_ok = hecke_mass_orbit_deficit_checked(result, covered, group, orders, 2,
                                                    expected_total) == HECKE_MASS_OK &&
                   mpq_cmp_ui(covered, 10, 1) == 0 && mpq_cmp_ui(result, 1, 1) == 0;

    mpq_clears(result, u, first, second, covered, expected_total, NULL);
    mpz_clears(four, six, q, k, rank, group, NULL);
    return mass_ok && hecke_ok && orbit_ok ? 0 : 1;
}
