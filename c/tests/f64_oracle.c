#include "../support/f64_oracle.h"

#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void require(int condition, const char *description)
{
    if (!condition) {
        fprintf(stderr, "%s\n", description);
        exit(EXIT_FAILURE);
    }
}

static void expect_bits(mpq_srcptr input, uint64_t expected)
{
    const double actual = hecke_mass_binary64_round(input);
    uint64_t bits;
    memcpy(&bits, &actual, sizeof bits);
    if (bits != expected) {
        fprintf(stderr, "rounded bits 0x%016" PRIx64 ", expected 0x%016" PRIx64 "\n",
                bits, expected);
        exit(EXIT_FAILURE);
    }
}

static void set_dyadic(mpq_ptr value, const char *coefficient, int exponent)
{
    require(mpz_set_str(mpq_numref(value), coefficient, 10) == 0,
            "invalid test coefficient");
    mpz_set_ui(mpq_denref(value), 1);
    if (exponent >= 0) {
        mpz_mul_2exp(mpq_numref(value), mpq_numref(value), (unsigned long)exponent);
    } else {
        mpz_mul_2exp(mpq_denref(value), mpq_denref(value), (unsigned long)(-exponent));
    }
    mpq_canonicalize(value);
}

static void test_rounding(mpq_ptr value)
{
    static const struct {
        const char *coefficient;
        int exponent;
        uint64_t expected;
    } dyadics[] = {
        {"0", 0, UINT64_C(0x0000000000000000)},
        {"9007199254740993", -53, UINT64_C(0x3ff0000000000000)},
        {"9007199254740995", -53, UINT64_C(0x3ff0000000000002)},
        {"18014398509481983", -53, UINT64_C(0x4000000000000000)},
        {"-9007199254740995", -53, UINT64_C(0xbff0000000000002)},
        {"1", -1076, UINT64_C(0x0000000000000000)},
        {"1", -1075, UINT64_C(0x0000000000000000)},
        {"-1", -1075, UINT64_C(0x8000000000000000)},
        {"3", -1076, UINT64_C(0x0000000000000001)},
        {"3", -1075, UINT64_C(0x0000000000000002)},
        {"9007199254740991", -1075, UINT64_C(0x0010000000000000)},
        {"9007199254740991", 971, UINT64_C(0x7fefffffffffffff)},
        {"36028797018963965", 969, UINT64_C(0x7fefffffffffffff)},
        {"18014398509481983", 970, UINT64_C(0x7ff0000000000000)},
        {"-18014398509481983", 970, UINT64_C(0xfff0000000000000)},
        {"1", 4096, UINT64_C(0x7ff0000000000000)},
        {"-1", -4096, UINT64_C(0x8000000000000000)},
    };
    for (size_t i = 0; i < sizeof dyadics / sizeof dyadics[0]; ++i) {
        set_dyadic(value, dyadics[i].coefficient, dyadics[i].exponent);
        expect_bits(value, dyadics[i].expected);
    }
    mpq_set_ui(value, 1, 10);
    expect_bits(value, UINT64_C(0x3fb999999999999a));
    mpq_set_ui(value, 1, 3);
    expect_bits(value, UINT64_C(0x3fd5555555555555));
}

static void test_adjacent_values(mpq_ptr value, mpq_ptr upper)
{
    uint64_t state = 957;
    for (size_t i = 0; i < 128; ++i) {
        state = state * UINT64_C(6364136223846793005) + 1;
        const uint64_t lower_bits = state % UINT64_C(0x7fefffffffffffff);
        const uint64_t upper_bits = lower_bits + 1;
        double lower_double, upper_double;
        memcpy(&lower_double, &lower_bits, sizeof lower_double);
        memcpy(&upper_double, &upper_bits, sizeof upper_double);
        mpq_set_d(value, lower_double);
        mpq_set_d(upper, upper_double);
        expect_bits(value, lower_bits);
        expect_bits(upper, upper_bits);

        /* The exact midpoint rounds to the endpoint with the even low bit. */
        mpq_add(value, value, upper);
        mpq_div_2exp(value, value, 1);
        expect_bits(value, (lower_bits & 1) == 0 ? lower_bits : upper_bits);
    }
}

static void test_exact_sums(mpq_ptr value, mpq_ptr expected)
{
    const uint32_t orders[] = {6, 0, 15};
    require(hecke_mass_exact_reciprocal_sum(value, orders, 3), "reciprocal sum failed");
    require(mpq_cmp_ui(value, 7, 30) == 0, "reciprocal sum should be 7/30");
    require(!hecke_mass_exact_reciprocal_sum(value, NULL, 1), "null orders accepted");
    require(mpq_cmp_ui(value, 7, 30) == 0, "invalid reciprocal input changed output");
    require(hecke_mass_exact_reciprocal_sum(value, NULL, 0), "empty reciprocal sum failed");
    require(mpq_sgn(value) == 0, "empty reciprocal sum should be zero");
    const uint32_t large_order[] = {UINT32_MAX};
    require(hecke_mass_exact_reciprocal_sum(value, large_order, 1), "large order failed");
    require(mpq_cmp_ui(value, 1, UINT32_MAX) == 0, "large order lost precision");

    const double weights[] = {1, 1, 1};
    const double samples[] = {0x1p53, 1, -0x1p53};
    require(hecke_mass_exact_weighted_sum(value, weights, samples, 3), "weighted sum failed");
    require(mpq_cmp_ui(value, 1, 1) == 0, "small term lost to cancellation");

    const double precise_weights[] = {0x1.0000000000001p0, 1};
    const double precise_samples[] = {0x1.ffffffffffffep-1, -1};
    require(hecke_mass_exact_weighted_sum(value, precise_weights, precise_samples, 2),
            "exact product failed");
    set_dyadic(expected, "-1", -104);
    require(mpq_equal(value, expected), "weighted products were rounded before summation");

    const double invalid_samples[] = {2, NAN};
    require(!hecke_mass_exact_weighted_sum(value, weights, invalid_samples, 2),
            "nonfinite samples accepted");
    require(mpq_equal(value, expected), "invalid weighted input changed output");
    require(!hecke_mass_exact_weighted_sum(value, NULL, samples, 1), "null weights accepted");
    require(mpq_equal(value, expected), "null weighted input changed output");
    require(hecke_mass_exact_weighted_sum(value, NULL, NULL, 0), "empty weighted sum failed");
    require(mpq_sgn(value) == 0, "empty weighted sum should be zero");
}

int main(void)
{
    mpq_t value, expected;
    mpq_inits(value, expected, NULL);
    test_rounding(value);
    test_adjacent_values(value, expected);
    test_exact_sums(value, expected);
    mpq_clears(value, expected, NULL);
    return EXIT_SUCCESS;
}
