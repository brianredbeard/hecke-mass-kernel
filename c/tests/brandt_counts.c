#include <hecke_mass/brandt.h>

#include <inttypes.h>
#include <stdio.h>

static size_t scalar_count(const uint32_t *destinations, size_t count, uint32_t target)
{
    size_t hits = 0;
    for (size_t i = 0; i < count; ++i) {
        hits += destinations[i] == target;
    }
    return hits;
}

static int check_count(const uint32_t *row, size_t length, uint32_t target, size_t expected)
{
    const size_t actual = hecke_mass_brandt_count_u32(row, length, target);
    if (actual == expected) {
        return 1;
    }
    fprintf(stderr, "Target %" PRIu32 " in %zu labels: got %zu, expected %zu\n",
            target, length, actual, expected);
    return 0;
}

int main(void)
{
    // Gross's level-11 degree-2 rows, with classes ordered by j = 1, 0.
    const uint32_t level11[][3] = {{1, 1, 0}, {0, 0, 0}};
    const size_t counts11[][2] = {{1, 2}, {3, 0}};
    for (size_t row = 0; row < 2; ++row) {
        for (uint32_t target = 0; target < 2; ++target) {
            if (!check_count(level11[row], 3, target, counts11[row][target])) {
                return 1;
            }
        }
    }

    // The modular-23-2 entry in HeckeMassKernel/ReplayedCases.lean.
    const uint32_t level23[][3] = {{1, 0, 1}, {1, 2, 0}, {1, 1, 1}};
    const size_t counts23[][3] = {{1, 2, 0}, {1, 1, 1}, {0, 3, 0}};
    for (size_t row = 0; row < 3; ++row) {
        for (uint32_t target = 0; target < 3; ++target) {
            if (!check_count(level23[row], 3, target, counts23[row][target])) {
                return 1;
            }
        }
    }

    // Test vector tails, multiple chunks and a nonzero starting offset.
    enum { capacity = 257 };
    uint32_t mixed[capacity + 1], repeated[capacity];
    const uint32_t labels[] = {0, 1, UINT32_C(0x80000000), UINT32_MAX, UINT32_MAX};
    for (size_t i = 0; i < capacity + 1; ++i) {
        mixed[i] = labels[i % (sizeof labels / sizeof labels[0])];
    }
    for (size_t i = 0; i < capacity; ++i) {
        repeated[i] = UINT32_MAX;
    }

    if (!check_count(NULL, 0, UINT32_MAX, 0) ||
        !check_count(repeated, capacity, UINT32_MAX, capacity)) {
        return 1;
    }
    const uint32_t targets[] = {0, 1, 2, UINT32_C(0x80000000), UINT32_MAX};
    for (size_t length = 0; length <= capacity; ++length) {
        for (size_t i = 0; i < sizeof targets / sizeof targets[0]; ++i) {
            const uint32_t target = targets[i];
            if (!check_count(mixed + 1, length, target, scalar_count(mixed + 1, length, target))) {
                return 1;
            }
        }
    }

    puts("Brandt counts verified at level 11 and level 23");
    return 0;
}
