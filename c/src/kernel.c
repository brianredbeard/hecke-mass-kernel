#include <hecke_mass/kernel.h>

static int valid_nonneg_mpz(mpz_srcptr value)
{
    return value != NULL && mpz_sgn(value) >= 0;
}

static int valid_mpq(mpq_srcptr value)
{
    return value != NULL && mpz_sgn(mpq_denref(value)) > 0;
}

/* Balanced binary-splitting sum of reciprocals orders[lo..hi). */
static void sum_reciprocals_range(mpq_ptr out, const mpz_srcptr orders[],
                                  size_t lo, size_t hi)
{
    size_t len = hi - lo;
    if (len == 0) {
        mpq_set_ui(out, 0, 1);
        return;
    }
    if (len == 1) {
        if (mpz_sgn(orders[lo]) == 0) {
            mpq_set_ui(out, 0, 1);
        } else {
            mpz_set_ui(mpq_numref(out), 1);
            mpz_set(mpq_denref(out), orders[lo]);
        }
        return;
    }

    size_t mid = lo + len / 2;
    mpq_t right;
    mpq_init(right);
    sum_reciprocals_range(out, orders, lo, mid);
    sum_reciprocals_range(right, orders, mid, hi);
    mpq_add(out, out, right);
    mpq_clear(right);
}

/* Balanced binary-splitting sum of samples[lo..hi). */
static void sum_samples_range(mpq_ptr out, const mpq_srcptr samples[],
                              size_t lo, size_t hi)
{
    size_t len = hi - lo;
    if (len == 0) {
        mpq_set_ui(out, 0, 1);
        return;
    }
    if (len == 1) {
        mpq_set(out, samples[lo]);
        return;
    }

    size_t mid = lo + len / 2;
    mpq_t right;
    mpq_init(right);
    sum_samples_range(out, samples, lo, mid);
    sum_samples_range(right, samples, mid, hi);
    mpq_add(out, out, right);
    mpq_clear(right);
}

static void natural_power(mpz_ptr result, mpz_srcptr base, mpz_srcptr exponent)
{
    if (mpz_sgn(exponent) == 0 || mpz_cmp_ui(base, 1) == 0) {
        mpz_set_ui(result, 1);
        return;
    }
    if (mpz_fits_ulong_p(exponent)) {
        unsigned long exp_ui = mpz_get_ui(exponent);
        if (mpz_cmp_ui(base, 2) == 0) {
            mpz_set_ui(result, 1);
            mpz_mul_2exp(result, result, exp_ui);
        } else {
            mpz_pow_ui(result, base, exp_ui);
        }
        return;
    }

    mpz_set_ui(result, 1);
    for (size_t bits = mpz_sizeinbase(exponent, 2); bits != 0; --bits) {
        mpz_mul(result, result, result);
        if (mpz_tstbit(exponent, bits - 1)) {
            mpz_mul(result, result, base);
        }
    }
}

hecke_mass_status hecke_mass_class_mass_checked(mpq_ptr result,
                                                const mpz_srcptr orders[],
                                                size_t count)
{
    if (result == NULL || (count != 0 && orders == NULL)) {
        return HECKE_MASS_ERR_INVALID_ARGUMENT;
    }
    for (size_t i = 0; i < count; ++i) {
        if (!valid_nonneg_mpz(orders[i])) {
            return HECKE_MASS_ERR_INVALID_ARGUMENT;
        }
    }

    mpq_t sum;
    mpq_init(sum);
    sum_reciprocals_range(sum, orders, 0, count);
    mpq_swap(result, sum);
    mpq_clear(sum);
    return HECKE_MASS_OK;
}

void hecke_mass_class_mass(mpq_ptr result, const mpz_srcptr orders[], size_t count)
{
    if (hecke_mass_class_mass_checked(result, orders, count) != HECKE_MASS_OK &&
        result != NULL) {
        mpq_set_ui(result, 0, 1);
    }
}

hecke_mass_status hecke_mass_hecke_checked(mpq_ptr result, mpq_srcptr u,
                                           mpz_srcptr q, mpz_srcptr k,
                                           mpz_srcptr rank,
                                           const mpq_srcptr samples[],
                                           size_t count)
{
    if (result == NULL || !valid_mpq(u) || !valid_nonneg_mpz(q) ||
        !valid_nonneg_mpz(k) || !valid_nonneg_mpz(rank) ||
        (count != 0 && samples == NULL)) {
        return HECKE_MASS_ERR_INVALID_ARGUMENT;
    }
    for (size_t i = 0; i < count; ++i) {
        if (!valid_mpq(samples[i])) {
            return HECKE_MASS_ERR_INVALID_ARGUMENT;
        }
    }

    if (mpq_sgn(u) == 0 || count == 0) {
        mpq_set_ui(result, 0, 1);
        return HECKE_MASS_OK;
    }

    mpz_t exponent, power, factor;
    mpq_t sum;
    mpz_inits(exponent, power, factor, NULL);
    mpq_init(sum);

    mpz_fdiv_q_2exp(exponent, rank, 1);
    mpz_mul(exponent, k, exponent);

    if (mpz_sgn(q) != 0 || mpz_sgn(exponent) == 0) {
        sum_samples_range(sum, samples, 0, count);
        if (mpq_sgn(sum) != 0) {
            mpq_div(sum, sum, u);
            natural_power(power, q, exponent);
            if (mpz_cmp_ui(power, 1) != 0) {
                mpz_gcd(factor, mpq_numref(sum), power);
                if (mpz_cmp_ui(factor, 1) != 0) {
                    mpz_divexact(mpq_numref(sum), mpq_numref(sum), factor);
                    mpz_divexact(power, power, factor);
                }
                mpz_mul(mpq_denref(sum), mpq_denref(sum), power);
            }
        }
    }

    mpq_swap(result, sum);
    mpq_clear(sum);
    mpz_clears(exponent, power, factor, NULL);
    return HECKE_MASS_OK;
}

void hecke_mass_hecke(mpq_ptr result, mpq_srcptr u, mpz_srcptr q, mpz_srcptr k,
                      mpz_srcptr rank, const mpq_srcptr samples[], size_t count)
{
    if (hecke_mass_hecke_checked(result, u, q, k, rank, samples, count) !=
            HECKE_MASS_OK &&
        result != NULL) {
        mpq_set_ui(result, 0, 1);
    }
}
