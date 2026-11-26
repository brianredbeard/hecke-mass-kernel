#ifndef HECKE_MASS_F64_CASES_H
#define HECKE_MASS_F64_CASES_H

#include <float.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#if FLT_RADIX != 2 || DBL_MANT_DIG != 53 || DBL_MAX_EXP != 1024
#error "Floating-point audit examples require binary64 double"
#endif

typedef char F64DoubleMustBe64Bits[sizeof(double) == sizeof(uint64_t) ? 1 : -1];

enum { F64_CASE_LENGTH = 4099 };

/* Round the exact rational workloads independently with Python Fraction. */
#define F64_HARMONIC_REFERENCE 0x1.1caab02d9bbe2p+3
#define F64_WIDE_REFERENCE 0x1.5df50e891eabfp+9
#define F64_CANCELLATION_REFERENCE 0x1.55cp-30

static inline void fill_harmonic_orders(uint32_t orders[F64_CASE_LENGTH])
{
    for (size_t i = 0; i < F64_CASE_LENGTH; ++i) {
        orders[i] = (uint32_t)(i + 1);
    }
}

static inline void fill_wide_orders(uint32_t orders[F64_CASE_LENGTH])
{
    const uint32_t pattern[] = {
        0, 1, 3, 7, 17, UINT32_C(0x80000000), UINT32_MAX, UINT32_C(4294967291), 65537,
    };
    const size_t pattern_length = sizeof(pattern) / sizeof(pattern[0]);
    for (size_t i = 0; i < F64_CASE_LENGTH; ++i) {
        orders[i] = pattern[i % pattern_length];
    }
}

static inline void fill_cancellation_inputs(double weights[F64_CASE_LENGTH],
                                            double samples[F64_CASE_LENGTH])
{
    /* The exact products of a complete triple are 2^53, 2^-40, -2^53. */
    const double weight_pattern[] = {2.0, -0.5, 4.0};
    const double sample_pattern[] = {0x1p52, -0x1p-39, -0x1p51};
    const size_t complete = F64_CASE_LENGTH - F64_CASE_LENGTH % 3;
    for (size_t i = 0; i < complete; ++i) {
        weights[i] = weight_pattern[i % 3];
        samples[i] = sample_pattern[i % 3];
    }
    for (size_t i = complete; i < F64_CASE_LENGTH; ++i) {
        weights[i] = -2.0;
        samples[i] = -0x1p-41;
    }
}

static inline uint64_t f64_bits(double value)
{
    uint64_t bits;
    memcpy(&bits, &value, sizeof(bits));
    return bits;
}

/* Map the finite binary64 values to consecutive integers with one shared zero. */
static inline uint64_t f64_key(double value)
{
    const uint64_t sign = UINT64_C(1) << 63;
    const uint64_t bits = f64_bits(value);
    const uint64_t magnitude = bits & ~sign;
    return bits & sign ? sign - magnitude : sign + magnitude;
}

static inline uint64_t f64_ulp_distance(double left, double right)
{
    const uint64_t a = f64_key(left);
    const uint64_t b = f64_key(right);
    return a < b ? b - a : a - b;
}

#endif
