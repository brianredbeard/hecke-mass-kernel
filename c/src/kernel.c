#include <hecke_mass/kernel.h>

void hecke_mass_class_mass(mpq_ptr result, const mpz_srcptr orders[], size_t count)
{
    mpq_t sum, reciprocal;
    mpq_inits(sum, reciprocal, NULL);
    mpz_set_ui(mpq_numref(reciprocal), 1);

    for (size_t i = 0; i < count; ++i) {
        if (mpz_sgn(orders[i]) != 0) {
            mpz_set(mpq_denref(reciprocal), orders[i]);
            mpq_add(sum, sum, reciprocal);
        }
    }

    mpq_swap(result, sum);
    mpq_clears(sum, reciprocal, NULL);
}

static void natural_power(mpz_ptr result, mpz_srcptr base, mpz_srcptr exponent)
{
    mpz_set_ui(result, 1);
    if (mpz_cmp_ui(base, 1) == 0) {
        return;
    }

    for (size_t bits = mpz_sizeinbase(exponent, 2); bits != 0; --bits) {
        mpz_mul(result, result, result);
        if (mpz_tstbit(exponent, bits - 1)) {
            mpz_mul(result, result, base);
        }
    }
}

void hecke_mass_hecke(mpq_ptr result, mpq_srcptr u, mpz_srcptr q, mpz_srcptr k,
                      mpz_srcptr rank, const mpq_srcptr samples[], size_t count)
{
    mpz_t exponent;
    mpq_t sum, power;
    mpz_init(exponent);
    mpq_inits(sum, power, NULL);
    mpz_fdiv_q_2exp(exponent, rank, 1);
    mpz_mul(exponent, k, exponent);

    if (mpq_sgn(u) != 0 && (mpz_sgn(q) != 0 || mpz_sgn(exponent) == 0)) {
        for (size_t i = 0; i < count; ++i) {
            mpq_add(sum, sum, samples[i]);
        }
        if (mpq_sgn(sum) != 0) {
            natural_power(mpq_numref(power), q, exponent);
            mpq_div(sum, sum, u);
            mpq_div(sum, sum, power);
        }
    }

    mpq_swap(result, sum);
    mpq_clears(sum, power, NULL);
    mpz_clear(exponent);
}
