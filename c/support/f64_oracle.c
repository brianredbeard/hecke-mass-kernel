#include "f64_oracle.h"

#include <hecke_mass/kernel.h>

#include <float.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

#if FLT_RADIX != 2 || DBL_MANT_DIG != 53 || DBL_MIN_EXP != -1021 || DBL_MAX_EXP != 1024
#error "The floating-point oracle requires IEEE 754 binary64 doubles"
#endif
typedef char binary64_size_check[sizeof(double) == sizeof(uint64_t) ? 1 : -1];

enum {
    FRACTION_BITS = 52,
    EXPONENT_BIAS = 1023,
    MIN_NORMAL_EXPONENT = -1022,
    MAX_NORMAL_EXPONENT = 1023,
    SUBNORMAL_SHIFT = 1074
};

static double binary64(uint64_t bits)
{
    double result;
    memcpy(&result, &bits, sizeof result);
    return result;
}

double hecke_mass_binary64_round(mpq_srcptr value)
{
    const int sign = mpq_sgn(value);
    if (sign == 0) {
        return 0.0;
    }
    const uint64_t sign_bit = sign < 0 ? UINT64_C(1) << 63 : 0;
    const uint64_t infinity = UINT64_C(0x7ff0000000000000);
    const size_t numerator_bits = mpz_sizeinbase(mpq_numref(value), 2);
    const size_t denominator_bits = mpz_sizeinbase(mpq_denref(value), 2);

    /* The bit-length difference is either floor(log2(|value|)) or one more. */
    int exponent;
    if (numerator_bits >= denominator_bits) {
        const size_t difference = numerator_bits - denominator_bits;
        if (difference > MAX_NORMAL_EXPONENT + 1) {
            return binary64(sign_bit | infinity);
        }
        exponent = (int)difference;
    } else {
        const size_t difference = denominator_bits - numerator_bits;
        if (difference > SUBNORMAL_SHIFT + 1) {
            return binary64(sign_bit);
        }
        exponent = -(int)difference;
    }

    mpz_t numerator, scaled;
    mpz_inits(numerator, scaled, NULL);
    mpz_abs(numerator, mpq_numref(value));
    mpz_srcptr denominator = mpq_denref(value);
    int comparison;
    if (exponent >= 0) {
        mpz_mul_2exp(scaled, denominator, (mp_bitcnt_t)exponent);
        comparison = mpz_cmp(numerator, scaled);
    } else {
        mpz_mul_2exp(scaled, numerator, (mp_bitcnt_t)(-exponent));
        comparison = mpz_cmp(scaled, denominator);
    }
    exponent -= comparison < 0;
    if (exponent > MAX_NORMAL_EXPONENT) {
        mpz_clears(numerator, scaled, NULL);
        return binary64(sign_bit | infinity);
    }

    /* Divide in units of the least significant bit of the resulting value. */
    const int subnormal = exponent < MIN_NORMAL_EXPONENT;
    const int shift = subnormal ? SUBNORMAL_SHIFT : FRACTION_BITS - exponent;
    mpz_srcptr dividend = numerator;
    mpz_srcptr divisor = denominator;
    if (shift >= 0) {
        mpz_mul_2exp(scaled, numerator, (mp_bitcnt_t)shift);
        dividend = scaled;
    } else {
        mpz_mul_2exp(scaled, denominator, (mp_bitcnt_t)(-shift));
        divisor = scaled;
    }

    mpz_t quotient, remainder;
    mpz_inits(quotient, remainder, NULL);
    mpz_tdiv_qr(quotient, remainder, dividend, divisor);
    mpz_mul_2exp(remainder, remainder, 1);
    comparison = mpz_cmp(remainder, divisor);
    if (comparison > 0 || (comparison == 0 && mpz_odd_p(quotient))) {
        mpz_add_ui(quotient, quotient, 1);
    }

    uint64_t significand = 0;
    /* The rounded quotient fits in one uint64_t even if unsigned long is narrower. */
    mpz_export(&significand, NULL, 1, sizeof significand, 0, 0, quotient);
    mpz_clears(quotient, remainder, numerator, scaled, NULL);

    const uint64_t hidden_bit = UINT64_C(1) << FRACTION_BITS;
    if (subnormal) {
        /* A carry into the hidden bit encodes the smallest normal value. */
        return binary64(sign_bit | significand);
    }
    if (significand == 2 * hidden_bit) {
        significand >>= 1;
        ++exponent;
    }
    const uint64_t exponent_bits = (uint64_t)(exponent + EXPONENT_BIAS) << FRACTION_BITS;
    return binary64(sign_bit | exponent_bits | (significand & (hidden_bit - 1)));
}

int hecke_mass_exact_reciprocal_sum(mpq_ptr out, const uint32_t *orders, size_t count)
{
    if (out == NULL || (count != 0 && orders == NULL) ||
        count > SIZE_MAX / sizeof(mpz_t) || count > SIZE_MAX / sizeof(mpz_srcptr)) {
        return 0;
    }
    if (count == 0) {
        mpq_set_ui(out, 0, 1);
        return 1;
    }

    mpz_t *integers = malloc(count * sizeof *integers);
    mpz_srcptr *references = malloc(count * sizeof *references);
    if (integers == NULL || references == NULL) {
        free(integers);
        free(references);
        return 0;
    }
    for (size_t i = 0; i < count; ++i) {
        mpz_init_set_ui(integers[i], orders[i]);
        references[i] = integers[i];
    }
    const hecke_mass_status status = hecke_mass_class_mass_checked(out, references, count);
    for (size_t i = 0; i < count; ++i) {
        mpz_clear(integers[i]);
    }
    free(integers);
    free(references);
    return status == HECKE_MASS_OK;
}

int hecke_mass_exact_weighted_sum(mpq_ptr out, const double *weights,
                                 const double *samples, size_t count)
{
    if (out == NULL || (count != 0 && (weights == NULL || samples == NULL))) {
        return 0;
    }

    mpq_t sum, weight, sample;
    mpq_inits(sum, weight, sample, NULL);
    int valid = 1;
    for (size_t i = 0; i < count; ++i) {
        if (!isfinite(weights[i]) || !isfinite(samples[i])) {
            valid = 0;
            break;
        }
        mpq_set_d(weight, weights[i]);
        mpq_set_d(sample, samples[i]);
        mpq_mul(weight, weight, sample);
        mpq_add(sum, sum, weight);
    }
    if (valid) {
        mpq_swap(out, sum);
    }
    mpq_clears(sum, weight, sample, NULL);
    return valid;
}
