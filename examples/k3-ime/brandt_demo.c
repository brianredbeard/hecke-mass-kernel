#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <inttypes.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <unistd.h>

enum { CLASSES = 3, TILE_ROWS = 4, TILE_DEPTH = 8, UNSUPPORTED = 77 };

/* Level-23 cases modular-23-2 and modular-23-3 in ReplayedCases.lean. */
static const int8_t t2[CLASSES][CLASSES] = {
    {1, 2, 0}, {1, 1, 1}, {0, 3, 0},
};
static const int8_t t3[CLASSES][CLASSES] = {
    {0, 2, 2}, {1, 3, 0}, {3, 0, 1},
};

extern unsigned long ime_vlenb(void);
extern void ime_multiply(const int8_t *left, const int8_t *right_transposed,
                         int32_t *product);

static int multiply_and_check(const int8_t left[CLASSES][CLASSES],
                              const int8_t right[CLASSES][CLASSES],
                              int32_t product[TILE_ROWS][TILE_ROWS])
{
    int8_t packed_left[TILE_ROWS][TILE_DEPTH] = {{0}};
    int8_t packed_right[TILE_ROWS][TILE_DEPTH] = {{0}};
    for (size_t row = 0; row < CLASSES; ++row) {
        for (size_t col = 0; col < CLASSES; ++col) {
            packed_left[row][col] = left[row][col];
            packed_right[col][row] = right[row][col];
        }
    }

    ime_multiply(&packed_left[0][0], &packed_right[0][0], &product[0][0]);

    for (size_t row = 0; row < TILE_ROWS; ++row) {
        for (size_t col = 0; col < TILE_ROWS; ++col) {
            int32_t expected = 0;
            for (size_t k = 0; k < TILE_DEPTH; ++k)
                expected += packed_left[row][k] * packed_right[col][k];
            if (product[row][col] != expected) {
                fprintf(stderr, "Tile entry (%zu, %zu) is %" PRId32
                        ", expected %" PRId32 "\n",
                        row, col, product[row][col], expected);
                return 1;
            }
        }
    }
    return 0;
}

static int demonstrate(void)
{
    unsigned long vlenb = ime_vlenb();
    if (vlenb != 32) {
        fprintf(stderr, "This demo requires 256-bit vector registers. Found %lu bits.\n",
                8 * vlenb);
        return UNSUPPORTED;
    }

    int32_t forward[TILE_ROWS][TILE_ROWS], reverse[TILE_ROWS][TILE_ROWS];
    if (multiply_and_check(t2, t3, forward) || multiply_and_check(t3, t2, reverse))
        return 1;
    for (size_t row = 0; row < CLASSES; ++row) {
        for (size_t col = 0; col < CLASSES; ++col) {
            if (forward[row][col] != reverse[row][col]) {
                fprintf(stderr, "Products differ at (%zu, %zu)\n", row, col);
                return 1;
            }
        }
    }
    puts("SpacemiT smt.vmadot, VLEN=256, INT8 inputs and INT32 accumulation");
    puts("Level 23 T2*T3 = T3*T2, both checked against scalar multiplication:");
    for (size_t row = 0; row < CLASSES; ++row)
        printf("[%" PRId32 " %" PRId32 " %" PRId32 "]\n",
               forward[row][0], forward[row][1], forward[row][2]);
    return 0;
}

int main(void)
{
    /* Isolate RVV and vendor instruction faults in the child. */
    struct rlimit no_core = {0, 0};
    if (setrlimit(RLIMIT_CORE, &no_core) == -1) {
        perror("setrlimit");
        return 1;
    }
    pid_t child = fork();
    if (child < 0) {
        perror("fork");
        return 1;
    }
    if (child == 0)
        return demonstrate();

    int status;
    pid_t waited;
    do {
        waited = waitpid(child, &status, 0);
    } while (waited == -1 && errno == EINTR);
    if (waited == -1) {
        perror("waitpid");
        return 1;
    }
    if (WIFEXITED(status))
        return WEXITSTATUS(status);
    if (WIFSIGNALED(status) && WTERMSIG(status) == SIGILL) {
        fputs("An RVV or SpacemiT IME instruction raised SIGILL.\n", stderr);
        return UNSUPPORTED;
    }
    fputs("The matrix demonstration process ended unexpectedly.\n", stderr);
    return 1;
}
