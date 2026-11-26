#include <hecke_mass/f64.h>

#include "f64_cases.h"

#include <fenv.h>
#include <inttypes.h>
#include <math.h>
#include <stdio.h>

typedef struct {
    double scalar;
    double ordered;
    double unordered;
} Results;

static Results reciprocal_results(const uint32_t *orders, size_t count)
{
    return (Results){
        hecke_mass_reciprocal_sum_scalar_f64(orders, count),
        hecke_mass_reciprocal_sum_ordered_f64(orders, count),
        hecke_mass_reciprocal_sum_unordered_f64(orders, count),
    };
}

static Results weighted_results(const double *weights, const double *samples, size_t count)
{
    return (Results){
        hecke_mass_weighted_sum_scalar_f64(weights, samples, count),
        hecke_mass_weighted_sum_ordered_f64(weights, samples, count),
        hecke_mass_weighted_sum_unordered_f64(weights, samples, count),
    };
}

static int check_exact(const char *name, size_t length, Results result, double expected)
{
    const uint64_t expected_bits = f64_bits(expected);
    if (f64_bits(result.scalar) == expected_bits && f64_bits(result.ordered) == expected_bits &&
        f64_bits(result.unordered) == expected_bits) {
        return 1;
    }
    fprintf(stderr, "%s at %zu entries expected %a, got scalar %a, ordered %a, unordered %a\n",
            name, length, expected, result.scalar, result.ordered, result.unordered);
    return 0;
}

static int exact_cases(void)
{
    if (!check_exact("empty reciprocals", 0, reciprocal_results(NULL, 0), 0.0) ||
        !check_exact("empty weighted sum", 0, weighted_results(NULL, NULL, 0), 0.0)) {
        return 0;
    }

    /* Exercise zero, unaligned starts, and every tail through 257 elements. */
    enum { CAPACITY = 257 };
    uint32_t orders[CAPACITY + 1] = {0};
    double weights[CAPACITY + 1] = {0};
    double samples[CAPACITY + 1] = {0};
    double mass = 0.0;
    double dot = 0.0;
    const uint32_t order_pattern[] = {0, 2, 4, 8};
    const double reciprocal_pattern[] = {0.0, 0.5, 0.25, 0.125};
    const double weight_pattern[] = {1.0, -2.0, 0.5, 4.0};
    const double sample_pattern[] = {0.0, 0.5, 0.5, 2.0};
    const double product_pattern[] = {0.0, -1.0, 0.25, 8.0};
    for (size_t count = 1; count <= CAPACITY; ++count) {
        const size_t i = (count - 1) % 4;
        orders[count] = order_pattern[i];
        weights[count] = weight_pattern[i];
        samples[count] = sample_pattern[i];
        mass += reciprocal_pattern[i];
        dot += product_pattern[i];
        if (!check_exact("reciprocal tail", count, reciprocal_results(orders + 1, count), mass) ||
            !check_exact("weighted tail", count,
                         weighted_results(weights + 1, samples + 1, count), dot)) {
            return 0;
        }
    }

    const uint32_t zeros[] = {0, 0, 0};
    if (feclearexcept(FE_ALL_EXCEPT) != 0 ||
        !check_exact("zero orders", 3, reciprocal_results(zeros, 3), 0.0) ||
        fetestexcept(FE_DIVBYZERO | FE_INVALID)) {
        fputs("zero-order reciprocals must avoid division by zero and invalid operations\n", stderr);
        return 0;
    }

    /* (1+2^-27)(1-2^-27) rounds to 1 before addition. A fused multiply-add gives -2^-54. */
    const double fused_weights[] = {-1.0, 0x1.0000002p0};
    const double fused_samples[] = {1.0, 0x1.ffffffcp-1};
    return check_exact("separately rounded products", 2,
                       weighted_results(fused_weights, fused_samples, 2), 0.0);
}

static int report(const char *name, Results result, double reference)
{
    if (!isfinite(result.scalar) || !isfinite(result.ordered) || !isfinite(result.unordered) ||
        f64_bits(result.scalar) != f64_bits(result.ordered)) {
        fprintf(stderr, "%s expected finite results and the ordered scalar result, got %a, %a, %a\n",
                name, result.scalar, result.ordered, result.unordered);
        return 0;
    }
    printf("%s reference=%a scalar_ulp=%" PRIu64 " ordered_ulp=%" PRIu64
           " unordered_ulp=%" PRIu64 " scalar_abs_rounded=%.17g"
           " ordered_abs_rounded=%.17g unordered_abs_rounded=%.17g\n",
           name, reference, f64_ulp_distance(result.scalar, reference),
           f64_ulp_distance(result.ordered, reference), f64_ulp_distance(result.unordered, reference),
           fabs(result.scalar - reference), fabs(result.ordered - reference),
           fabs(result.unordered - reference));
    return 1;
}

static int check_reciprocals(const char *name, const uint32_t *orders, double reference)
{
    const Results result = reciprocal_results(orders, F64_CASE_LENGTH);
    if (!report(name, result, reference)) {
        return 0;
    }
    /* Each leaf has one rounded divide and at most count rounded additions.
       This conservative limit allows a change in summation tree or VLEN. */
    const uint64_t limit = 2 * F64_CASE_LENGTH + 4;
    if (f64_ulp_distance(result.scalar, reference) > limit ||
        f64_ulp_distance(result.unordered, reference) > limit) {
        fprintf(stderr, "%s exceeds %" PRIu64 " ULPs\n", name, limit);
        return 0;
    }
    return 1;
}

int main(void)
{
    if (!exact_cases()) {
        return 1;
    }

    uint32_t orders[F64_CASE_LENGTH];
    fill_harmonic_orders(orders);
    if (!check_reciprocals("harmonic", orders, F64_HARMONIC_REFERENCE)) {
        return 1;
    }
    fill_wide_orders(orders);
    if (!check_reciprocals("wide-with-zeros", orders, F64_WIDE_REFERENCE)) {
        return 1;
    }

    double weights[F64_CASE_LENGTH], samples[F64_CASE_LENGTH];
    fill_cancellation_inputs(weights, samples);
    const Results result = weighted_results(weights, samples, F64_CASE_LENGTH);
    const double reference = F64_CANCELLATION_REFERENCE;
    if (!report("signed-cancellation", result, reference)) {
        return 1;
    }
    /* Input order loses each triple's small term and retains the final term.
       In any tree, the sum of absolute products is less than
       (2 * triples + 1) * 2^53. For n additions, gamma_n < 2 * n * 2^-53.
       The absolute bound therefore also permits wider intermediates. */
    const double limit = 2.0 * F64_CASE_LENGTH * (2 * (F64_CASE_LENGTH / 3) + 1);
    if (result.scalar != 0x1p-40 || fabs(result.unordered - reference) > limit) {
        fputs("signed cancellation exceeded the case's absolute error bound\n", stderr);
        return 1;
    }
    return 0;
}
