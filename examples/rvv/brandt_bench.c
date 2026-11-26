#define _POSIX_C_SOURCE 200809L

#include <hecke_mass/brandt.h>

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

typedef size_t (*count_fn)(const uint32_t *, size_t, uint32_t);

#if defined(__riscv_vector)
size_t hecke_mass_brandt_count_scalar_u32(const uint32_t *destinations,
                                          size_t count, uint32_t target);
#endif

static const struct {
    const char *name;
    count_fn count;
} backends[] = {
#if defined(__riscv_vector)
    {"scalar", hecke_mass_brandt_count_scalar_u32},
    {"RVV", hecke_mass_brandt_count_u32},
#else
    {"scalar", hecke_mass_brandt_count_u32},
#endif
};

static double monotonic_seconds(void)
{
    struct timespec time;
    if (clock_gettime(CLOCK_MONOTONIC, &time) != 0) {
        perror("clock_gettime");
        exit(EXIT_FAILURE);
    }
    return (double)time.tv_sec + (double)time.tv_nsec * 1e-9;
}

static void measure(const char *name, count_fn count, const uint32_t *destinations,
                    size_t length, uint32_t target, size_t expected)
{
    const size_t repetitions = 256;
    size_t checksum = 0;
    double start = monotonic_seconds();
    for (size_t i = 0; i < repetitions; ++i) {
        checksum += count(destinations, length, target);
    }
    double elapsed = monotonic_seconds() - start;
    if (checksum != expected * repetitions || elapsed <= 0) {
        fprintf(stderr, "%s count or timer check failed\n", name);
        exit(EXIT_FAILURE);
    }
    printf("%-6s %9.2f million destinations/s\n", name,
           (double)length * (double)repetitions / elapsed / 1e6);
}

int main(void)
{
    const size_t length = 1u << 20;
    const uint32_t target = 93;
    uint32_t *destinations = malloc(length * sizeof(*destinations));
    if (destinations == NULL) {
        perror("malloc");
        return EXIT_FAILURE;
    }

    uint32_t state = 957;
    size_t expected = 0;
    for (size_t i = 0; i < length; ++i) {
        state = state * UINT32_C(1664525) + UINT32_C(1013904223);
        destinations[i] = state >> 24;
        expected += destinations[i] == target;
    }

#if defined(__riscv_vector)
    unsigned long vlen_bytes;
    __asm__ volatile ("csrr %0, vlenb" : "=r" (vlen_bytes));
    printf("VLEN=%lu bits, ", vlen_bytes * 8);
#endif
    printf("%zu destinations, %zu matches\n", length, expected);

    const size_t backend_count = sizeof(backends) / sizeof(backends[0]);
    for (size_t trial = 0; trial < 6; ++trial) {
        for (size_t run = 0; run < backend_count; ++run) {
            const size_t backend = (trial + run) % backend_count;
            measure(backends[backend].name, backends[backend].count, destinations,
                    length, target, expected);
        }
    }
    free(destinations);
    return EXIT_SUCCESS;
}
