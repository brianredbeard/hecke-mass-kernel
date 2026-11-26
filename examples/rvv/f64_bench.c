#define _POSIX_C_SOURCE 200809L

#include <hecke_mass/f64.h>

#include "f64_cases.h"
#include "f64_oracle.h"

#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

enum { REPETITIONS = 2048, TRIALS = 5 };

typedef double (*reciprocal_fn)(const uint32_t *, size_t);
typedef double (*weighted_fn)(const double *, const double *, size_t);

typedef struct {
    const char *name;
    reciprocal_fn reciprocal_sum;
    weighted_fn weighted_sum;
} Backend;

static const Backend backends[] = {
    {"scalar", hecke_mass_reciprocal_sum_scalar_f64, hecke_mass_weighted_sum_scalar_f64},
#ifdef HECKE_MASS_ENABLE_RVV
    {"ordered", hecke_mass_reciprocal_sum_ordered_f64, hecke_mass_weighted_sum_ordered_f64},
    {"unordered", hecke_mass_reciprocal_sum_unordered_f64, hecke_mass_weighted_sum_unordered_f64},
#endif
};

typedef struct {
    const char *name;
    const uint32_t *orders;
    const double *weights;
    const double *samples;
    double expected_reference;
} Workload;

static double monotonic_seconds(void)
{
    struct timespec time;
    if (clock_gettime(CLOCK_MONOTONIC, &time) != 0) {
        perror("clock_gettime");
        exit(EXIT_FAILURE);
    }
    return (double)time.tv_sec + (double)time.tv_nsec * 1e-9;
}

static double run_once(const Backend *backend, const Workload *workload)
{
    if (workload->orders != NULL) {
        return backend->reciprocal_sum(workload->orders, F64_CASE_LENGTH);
    }
    return backend->weighted_sum(workload->weights, workload->samples, F64_CASE_LENGTH);
}

static double measure(const Backend *backend, const Workload *workload, double expected)
{
    double result = 0.0;
    double start;
    if (workload->orders != NULL) {
        reciprocal_fn volatile sum = backend->reciprocal_sum;
        start = monotonic_seconds();
        for (size_t i = 0; i < REPETITIONS; ++i) {
            result = sum(workload->orders, F64_CASE_LENGTH);
        }
    } else {
        weighted_fn volatile sum = backend->weighted_sum;
        start = monotonic_seconds();
        for (size_t i = 0; i < REPETITIONS; ++i) {
            result = sum(workload->weights, workload->samples, F64_CASE_LENGTH);
        }
    }
    const double elapsed = monotonic_seconds() - start;
    if (f64_bits(result) != f64_bits(expected) || elapsed <= 0.0) {
        fprintf(stderr, "%s %s result changed or timer failed\n", workload->name, backend->name);
        exit(EXIT_FAILURE);
    }
    return (double)F64_CASE_LENGTH * REPETITIONS / elapsed / 1e6;
}

static int compare_rates(const void *left, const void *right)
{
    const double a = *(const double *)left;
    const double b = *(const double *)right;
    return (a > b) - (a < b);
}

static int benchmark(const Workload *workload)
{
    mpq_t exact, error;
    mpq_inits(exact, error, NULL);
    const int valid = workload->orders != NULL
        ? hecke_mass_exact_reciprocal_sum(exact, workload->orders, F64_CASE_LENGTH)
        : hecke_mass_exact_weighted_sum(exact, workload->weights, workload->samples,
                                        F64_CASE_LENGTH);
    if (!valid) {
        fprintf(stderr, "%s exact oracle failed\n", workload->name);
        mpq_clears(exact, error, NULL);
        return 0;
    }
    const double reference = hecke_mass_binary64_round(exact);
    if (f64_bits(reference) != f64_bits(workload->expected_reference)) {
        fprintf(stderr, "%s oracle gave %a, expected %a\n",
                workload->name, reference, workload->expected_reference);
        mpq_clears(exact, error, NULL);
        return 0;
    }
    printf("case=%s reference=%a\n", workload->name, reference);

    enum { BACKEND_COUNT = sizeof(backends) / sizeof(backends[0]) };
    double results[BACKEND_COUNT];
    double rates[BACKEND_COUNT][TRIALS];
    for (size_t i = 0; i < BACKEND_COUNT; ++i) {
        results[i] = run_once(&backends[i], workload);
        if (!isfinite(results[i])) {
            fprintf(stderr, "%s %s produced a non-finite result\n", workload->name, backends[i].name);
            mpq_clears(exact, error, NULL);
            return 0;
        }
    }
    for (size_t trial = 0; trial < TRIALS; ++trial) {
        for (size_t run = 0; run < BACKEND_COUNT; ++run) {
            const size_t i = (trial + run) % BACKEND_COUNT;
            rates[i][trial] = measure(&backends[i], workload, results[i]);
        }
    }
    for (size_t i = 0; i < BACKEND_COUNT; ++i) {
        qsort(rates[i], TRIALS, sizeof(rates[i][0]), compare_rates);
        mpq_set_d(error, results[i]);
        mpq_sub(error, error, exact);
        mpq_abs(error, error);
        printf("case=%s backend=%s result=%a ulps=%" PRIu64 " absolute_error=%.17g "
               "million_terms_per_second=%.2f\n",
               workload->name, backends[i].name, results[i],
               f64_ulp_distance(results[i], reference), hecke_mass_binary64_round(error),
               rates[i][TRIALS / 2]);
    }
    mpq_clears(exact, error, NULL);
    return 1;
}

int main(void)
{
#ifdef HECKE_MASS_ENABLE_RVV
    unsigned long vlen_bytes;
    __asm__ volatile ("csrr %0, vlenb" : "=r" (vlen_bytes));
    printf("build=rvv vlen_bits=%lu ", vlen_bytes * 8);
#else
    printf("build=scalar ");
#endif
    printf("terms=%d repetitions=%d trials=%d\n", F64_CASE_LENGTH, REPETITIONS, TRIALS);

    uint32_t harmonic[F64_CASE_LENGTH], wide[F64_CASE_LENGTH];
    double weights[F64_CASE_LENGTH], samples[F64_CASE_LENGTH];
    fill_harmonic_orders(harmonic);
    fill_wide_orders(wide);
    fill_cancellation_inputs(weights, samples);
    const Workload workloads[] = {
        {"harmonic", harmonic, NULL, NULL, F64_HARMONIC_REFERENCE},
        {"wide-with-zeros", wide, NULL, NULL, F64_WIDE_REFERENCE},
        {"signed-cancellation", NULL, weights, samples, F64_CANCELLATION_REFERENCE},
    };
    for (size_t i = 0; i < sizeof(workloads) / sizeof(workloads[0]); ++i) {
        if (!benchmark(&workloads[i])) {
            return EXIT_FAILURE;
        }
    }
    return EXIT_SUCCESS;
}
