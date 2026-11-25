#include <hecke_mass/kernel.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int set_rational(mpq_ptr value, const char *text)
{
    if (mpq_set_str(value, text, 10) != 0 || mpz_sgn(mpq_denref(value)) <= 0) {
        return 0;
    }
    mpq_canonicalize(value);
    return 1;
}

/* Read one line of arbitrary length; accepts a final line without '\n'. */
static char *read_line(FILE *stream, int *io_error)
{
    size_t capacity = 256;
    size_t length = 0;
    char *buffer = malloc(capacity);
    if (buffer == NULL) {
        *io_error = 1;
        return NULL;
    }

    for (;;) {
        int ch = fgetc(stream);
        if (ch == EOF) {
            if (ferror(stream)) {
                *io_error = 1;
                free(buffer);
                return NULL;
            }
            if (length == 0) {
                free(buffer);
                return NULL;
            }
            break;
        }
        if (length + 1 >= capacity) {
            size_t next = capacity * 2;
            char *grown = realloc(buffer, next);
            if (grown == NULL) {
                *io_error = 1;
                free(buffer);
                return NULL;
            }
            buffer = grown;
            capacity = next;
        }
        buffer[length++] = (char)ch;
        if (ch == '\n') {
            break;
        }
    }
    buffer[length] = '\0';
    return buffer;
}

static int evaluate_mass(mpq_ptr result, const char *args[], size_t count)
{
    mpz_t *orders = count ? calloc(count, sizeof(*orders)) : NULL;
    mpz_srcptr *inputs = count ? calloc(count, sizeof(*inputs)) : NULL;
    if (count != 0 && (orders == NULL || inputs == NULL)) {
        free(orders);
        free(inputs);
        return 0;
    }

    size_t initialized = 0;
    int valid = 1;
    while (valid && initialized < count) {
        mpz_init(orders[initialized]);
        inputs[initialized] = orders[initialized];
        valid = mpz_set_str(orders[initialized], args[initialized], 10) == 0 &&
                mpz_sgn(orders[initialized]) >= 0;
        ++initialized;
    }
    if (valid) {
        valid = hecke_mass_class_mass_checked(result, count ? inputs : NULL, count) ==
                HECKE_MASS_OK;
    }
    while (initialized != 0) {
        mpz_clear(orders[--initialized]);
    }
    free(orders);
    free(inputs);
    return valid;
}

static int evaluate_hecke(mpq_ptr result, const char *args[], size_t count)
{
    if (count < 4) {
        return 0;
    }
    size_t sample_count = count - 4;
    mpq_t *samples = sample_count ? calloc(sample_count, sizeof(*samples)) : NULL;
    mpq_srcptr *inputs = sample_count ? calloc(sample_count, sizeof(*inputs)) : NULL;
    if (sample_count != 0 && (samples == NULL || inputs == NULL)) {
        free(samples);
        free(inputs);
        return 0;
    }

    mpq_t u;
    mpz_t q, k, rank;
    mpq_init(u);
    mpz_inits(q, k, rank, NULL);
    int valid = set_rational(u, args[0]) &&
                mpz_set_str(q, args[1], 10) == 0 && mpz_sgn(q) >= 0 &&
                mpz_set_str(k, args[2], 10) == 0 && mpz_sgn(k) >= 0 &&
                mpz_set_str(rank, args[3], 10) == 0 && mpz_sgn(rank) >= 0;
    size_t initialized = 0;
    while (valid && initialized < sample_count) {
        mpq_init(samples[initialized]);
        inputs[initialized] = samples[initialized];
        valid = set_rational(samples[initialized], args[4 + initialized]);
        ++initialized;
    }
    if (valid) {
        valid = hecke_mass_hecke_checked(result, u, q, k, rank,
                                         sample_count ? inputs : NULL,
                                         sample_count) == HECKE_MASS_OK;
    }
    while (initialized != 0) {
        mpq_clear(samples[--initialized]);
    }
    mpz_clears(q, k, rank, NULL);
    mpq_clear(u);
    free(samples);
    free(inputs);
    return valid;
}

static int check_row(char *line)
{
    char *arguments = strchr(line, '\t');
    if (arguments == NULL) {
        return 0;
    }
    *arguments++ = '\0';
    char *expected_text = strchr(arguments, '\t');
    if (expected_text == NULL) {
        return 0;
    }
    *expected_text++ = '\0';
    expected_text[strcspn(expected_text, "\r\n")] = '\0';

    size_t capacity = 16;
    size_t count = 0;
    const char **args = malloc(capacity * sizeof(*args));
    if (args == NULL) {
        return 0;
    }

    for (char *token = strtok(arguments, " "); token != NULL;
         token = strtok(NULL, " ")) {
        if (count == capacity) {
            size_t next = capacity * 2;
            const char **grown = realloc(args, next * sizeof(*args));
            if (grown == NULL) {
                free(args);
                return 0;
            }
            args = grown;
            capacity = next;
        }
        args[count++] = token;
    }

    mpq_t result, expected;
    mpq_inits(result, expected, NULL);
    int evaluated = 0;
    if (strcmp(line, "mass") == 0) {
        evaluated = evaluate_mass(result, args, count);
    } else if (strcmp(line, "hecke") == 0) {
        evaluated = evaluate_hecke(result, args, count);
    }
    int matches = evaluated && set_rational(expected, expected_text) &&
                  mpq_equal(result, expected);
    mpq_clears(result, expected, NULL);
    free(args);
    return matches;
}

static int check_api_contracts(void)
{
    int ok = 1;
    mpz_t neg, pos, zero, q, k, rank;
    mpq_t out, u, s1, s2, bad;
    mpz_init_set_si(neg, -3);
    mpz_init_set_ui(pos, 4);
    mpz_init_set_ui(zero, 0);
    mpz_init_set_ui(q, 3);
    mpz_init_set_ui(k, 2);
    mpz_init_set_ui(rank, 5);
    mpq_inits(out, u, s1, s2, bad, NULL);
    mpq_set_si(out, 7, 1);
    mpq_set_si(u, -2, 3);
    mpq_set_si(s1, 1, 2);
    mpq_set_si(s2, 3, 4);
    mpz_set_si(mpq_numref(bad), 1);
    mpz_set_si(mpq_denref(bad), -2);

    /* Reject invalid arguments without mutating result. */
    const mpz_srcptr bad_orders[] = {pos, neg};
    ok = ok && hecke_mass_class_mass_checked(out, bad_orders, 2) ==
                   HECKE_MASS_ERR_INVALID_ARGUMENT;
    ok = ok && mpq_cmp_si(out, 7, 1) == 0;
    ok = ok && hecke_mass_class_mass_checked(out, NULL, 1) ==
                   HECKE_MASS_ERR_INVALID_ARGUMENT;
    ok = ok && hecke_mass_class_mass_checked(NULL, NULL, 0) ==
                   HECKE_MASS_ERR_INVALID_ARGUMENT;

    const mpq_srcptr good_samples[] = {s1, s2};
    const mpq_srcptr bad_samples[] = {s1, bad};
    ok = ok && hecke_mass_hecke_checked(out, bad, q, k, rank, good_samples, 2) ==
                   HECKE_MASS_ERR_INVALID_ARGUMENT;
    ok = ok && hecke_mass_hecke_checked(out, u, neg, k, rank, good_samples, 2) ==
                   HECKE_MASS_ERR_INVALID_ARGUMENT;
    ok = ok && hecke_mass_hecke_checked(out, u, q, neg, rank, good_samples, 2) ==
                   HECKE_MASS_ERR_INVALID_ARGUMENT;
    ok = ok && hecke_mass_hecke_checked(out, u, q, k, neg, good_samples, 2) ==
                   HECKE_MASS_ERR_INVALID_ARGUMENT;
    ok = ok && hecke_mass_hecke_checked(out, u, q, k, rank, bad_samples, 2) ==
                   HECKE_MASS_ERR_INVALID_ARGUMENT;
    ok = ok && hecke_mass_hecke_checked(out, u, q, k, rank, NULL, 1) ==
                   HECKE_MASS_ERR_INVALID_ARGUMENT;
    ok = ok && mpq_cmp_si(out, 7, 1) == 0;

    /* Pointer aliasing: result == u and result == samples[0]. */
    mpq_set(out, u);
    ok = ok && hecke_mass_hecke_checked(out, out, q, k, rank, good_samples, 2) ==
                   HECKE_MASS_OK;
    /* (-2/3)^-1 * 3^-4 * (1/2 + 3/4) = (-3/2) * (1/81) * (5/4) = -5/216 */
    ok = ok && mpq_cmp_si(out, -5, 216) == 0;

    mpq_set(out, s1);
    const mpq_srcptr aliased_samples[] = {out, s2};
    ok = ok && hecke_mass_hecke_checked(out, u, q, k, rank, aliased_samples, 2) ==
                   HECKE_MASS_OK;
    ok = ok && mpq_cmp_si(out, -5, 216) == 0;

    /* Permutation invariance of class_mass and hecke. */
    mpz_t d1, d2, d3, d4;
    mpz_init_set_ui(d1, 2);
    mpz_init_set_ui(d2, 3);
    mpz_init_set_ui(d3, 7);
    mpz_init_set_ui(d4, 43);
    const mpz_srcptr fwd[] = {d1, d2, d3, d4};
    const mpz_srcptr rev[] = {d4, d3, d2, d1};
    mpq_t m1, m2;
    mpq_inits(m1, m2, NULL);
    hecke_mass_class_mass(m1, fwd, 4);
    hecke_mass_class_mass(m2, rev, 4);
    ok = ok && mpq_equal(m1, m2) && mpq_cmp_ui(m1, 1805, 1806) == 0;

    const mpq_srcptr samples_rev[] = {s2, s1};
    hecke_mass_hecke(m1, u, q, k, rank, good_samples, 2);
    hecke_mass_hecke(m2, u, q, k, rank, samples_rev, 2);
    ok = ok && mpq_equal(m1, m2);

    /* Unchecked void wrapper zeros output safely on invalid input. */
    mpq_set_si(out, 9, 1);
    hecke_mass_class_mass(out, bad_orders, 2);
    ok = ok && mpq_sgn(out) == 0;

    mpq_clears(m1, m2, out, u, s1, s2, bad, NULL);
    mpz_clears(d1, d2, d3, d4, neg, pos, zero, q, k, rank, NULL);
    return ok;
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        return 1;
    }
    if (!check_api_contracts()) {
        fprintf(stderr, "C API contract checks failed\n");
        return 1;
    }
    FILE *fixtures = fopen(argv[1], "r");
    if (fixtures == NULL) {
        perror(argv[1]);
        return 1;
    }

    size_t rows = 0;
    int valid = 1;
    int io_error = 0;
    char *line = NULL;
    while (valid && (line = read_line(fixtures, &io_error)) != NULL) {
        ++rows;
        valid = check_row(line);
        free(line);
    }
    valid = valid && !io_error && !ferror(fixtures) && rows != 0;
    fclose(fixtures);
    if (!valid) {
        fprintf(stderr, "Kernel fixture failed at line %zu in %s\n", rows, argv[1]);
    }
    return valid ? 0 : 1;
}
