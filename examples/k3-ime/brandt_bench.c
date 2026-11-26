#define _POSIX_C_SOURCE 200809L

#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

enum {
    TILE_ROWS = 4,
    TILE_DEPTH = 8,
    TILE_COUNT = 128,
    PASSES = 8192,
    TRIALS = 6,
    UNSUPPORTED = 77
};

extern unsigned long ime_vlenb(void);
extern void ime_multiply(const int8_t *left, const int8_t *right_transposed,
                         int32_t *product);

typedef void (*tile_fn)(const int8_t *, const int8_t *, int32_t *);

/* Keep the same indirect call in the measured loop for either backend. */
static tile_fn volatile dispatch;

typedef struct {
    int8_t left[TILE_ROWS * TILE_DEPTH];
    int8_t right_transposed[TILE_ROWS * TILE_DEPTH];
    int32_t expected[TILE_ROWS * TILE_ROWS];
    int32_t product[TILE_ROWS * TILE_ROWS];
} Tile;

static void scalar_multiply(const int8_t *left, const int8_t *right_transposed,
                            int32_t *product)
{
    for (size_t row = 0; row < TILE_ROWS; ++row) {
        for (size_t col = 0; col < TILE_ROWS; ++col) {
            int32_t sum = 0;
            for (size_t k = 0; k < TILE_DEPTH; ++k) {
                sum += left[row * TILE_DEPTH + k] * right_transposed[col * TILE_DEPTH + k];
            }
            product[row * TILE_ROWS + col] = sum;
        }
    }
}

static int8_t next_byte(uint32_t *state)
{
    *state = *state * UINT32_C(1664525) + UINT32_C(1013904223);
    return (int8_t)((int32_t)(*state >> 24) - 128);
}

static double monotonic_seconds(void)
{
    struct timespec time;
    if (clock_gettime(CLOCK_MONOTONIC, &time) != 0) {
        perror("clock_gettime");
        exit(EXIT_FAILURE);
    }
    return (double)time.tv_sec + (double)time.tv_nsec * 1e-9;
}

static void check_products(const char *name, const Tile *tiles)
{
    for (size_t i = 0; i < TILE_COUNT; ++i) {
        if (memcmp(tiles[i].product, tiles[i].expected, sizeof(tiles[i].product)) != 0) {
            fprintf(stderr, "%s product mismatch at tile %zu\n", name, i);
            exit(EXIT_FAILURE);
        }
    }
}

static void measure(const char *name, tile_fn kernel, Tile *tiles)
{
    /* Make each sample prove it overwrote every output tile. */
    for (size_t i = 0; i < TILE_COUNT; ++i) {
        memset(tiles[i].product, 0x5a, sizeof(tiles[i].product));
    }
    dispatch = kernel;
    tile_fn multiply = dispatch;
    double start = monotonic_seconds();
    for (size_t pass = 0; pass < PASSES; ++pass) {
        for (size_t i = 0; i < TILE_COUNT; ++i) {
            multiply(tiles[i].left, tiles[i].right_transposed, tiles[i].product);
        }
    }
    double elapsed = monotonic_seconds() - start;
    check_products(name, tiles);
    if (elapsed <= 0) {
        fprintf(stderr, "Benchmark timer check failed\n");
        exit(EXIT_FAILURE);
    }
    printf("%-6s %9.2f ns/tile\n", name, elapsed * 1e9 / (TILE_COUNT * PASSES));
}

static void unavailable(int signal_number)
{
    (void)signal_number;
    static const char message[] = "An RVV or SpacemiT IME instruction raised SIGILL.\n";
    (void)write(STDERR_FILENO, message, sizeof(message) - 1);
    _Exit(UNSUPPORTED);
}

int main(void)
{
    struct sigaction action = {0};
    action.sa_handler = unavailable;
    if (sigemptyset(&action.sa_mask) != 0 || sigaction(SIGILL, &action, NULL) != 0) {
        perror("SIGILL handler");
        return EXIT_FAILURE;
    }
    unsigned long vlenb = ime_vlenb();
    if (vlenb != 32) {
        fprintf(stderr, "This benchmark requires 256-bit vector registers. Found %lu bits.\n",
                8 * vlenb);
        return UNSUPPORTED;
    }

    Tile tiles[TILE_COUNT];
    uint32_t state = 957;
    for (size_t i = 0; i < TILE_COUNT; ++i) {
        Tile *tile = &tiles[i];
        for (size_t j = 0; j < TILE_ROWS * TILE_DEPTH; ++j) {
            tile->left[j] = next_byte(&state);
            tile->right_transposed[j] = next_byte(&state);
        }
        scalar_multiply(tile->left, tile->right_transposed, tile->expected);
        ime_multiply(tile->left, tile->right_transposed, tile->product);
    }
    check_products("IME", tiles);

    printf("VLEN=%lu bits, %d packed tiles, %d calls per measurement\n",
           8 * vlenb, TILE_COUNT, TILE_COUNT * PASSES);
    const tile_fn kernels[] = {scalar_multiply, ime_multiply};
    const char *names[] = {"scalar", "IME"};
    for (size_t trial = 0; trial < TRIALS; ++trial) {
        size_t first = trial % 2;
        measure(names[first], kernels[first], tiles);
        measure(names[1 - first], kernels[1 - first], tiles);
    }
    return EXIT_SUCCESS;
}
