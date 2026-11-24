#include <hecke_mass/kernel.h>

#include <stdio.h>
#include <string.h>

enum { arg_capacity = 128 };

static int set_rational(mpq_ptr value, const char *text)
{
    if (mpq_set_str(value, text, 10) != 0 || mpz_sgn(mpq_denref(value)) <= 0) {
        return 0;
    }
    mpq_canonicalize(value);
    return 1;
}

static int evaluate_mass(mpq_ptr result, const char *args[], size_t count)
{
    mpz_t orders[arg_capacity];
    mpz_srcptr inputs[arg_capacity];
    size_t initialized = 0;
    int valid = 1;
    while (valid && initialized < count) {
        mpz_init(orders[initialized]);
        inputs[initialized] = orders[initialized];
        valid = mpz_set_str(orders[initialized], args[initialized], 10) == 0
            && mpz_sgn(orders[initialized]) >= 0;
        ++initialized;
    }
    if (valid) {
        hecke_mass_class_mass(result, count ? inputs : NULL, count);
    }
    while (initialized != 0) {
        mpz_clear(orders[--initialized]);
    }
    return valid;
}

static int evaluate_hecke(mpq_ptr result, const char *args[], size_t count)
{
    if (count < 4) {
        return 0;
    }
    mpq_t u, samples[arg_capacity];
    mpq_srcptr inputs[arg_capacity];
    mpz_t q, k, rank;
    mpq_init(u);
    mpz_inits(q, k, rank, NULL);
    int valid = set_rational(u, args[0])
        && mpz_set_str(q, args[1], 10) == 0 && mpz_sgn(q) >= 0
        && mpz_set_str(k, args[2], 10) == 0 && mpz_sgn(k) >= 0
        && mpz_set_str(rank, args[3], 10) == 0 && mpz_sgn(rank) >= 0;
    size_t initialized = 0;
    size_t sample_count = count - 4;
    while (valid && initialized < sample_count) {
        mpq_init(samples[initialized]);
        inputs[initialized] = samples[initialized];
        valid = set_rational(samples[initialized], args[4 + initialized]);
        ++initialized;
    }
    if (valid) {
        hecke_mass_hecke(result, u, q, k, rank, sample_count ? inputs : NULL, sample_count);
    }
    while (initialized != 0) {
        mpq_clear(samples[--initialized]);
    }
    mpz_clears(q, k, rank, NULL);
    mpq_clear(u);
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

    const char *args[arg_capacity];
    size_t count = 0;
    for (char *token = strtok(arguments, " "); token != NULL; token = strtok(NULL, " ")) {
        if (count == arg_capacity) {
            return 0;
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
    int matches = evaluated && set_rational(expected, expected_text) && mpq_equal(result, expected);
    mpq_clears(result, expected, NULL);
    return matches;
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        return 1;
    }
    FILE *fixtures = fopen(argv[1], "r");
    if (fixtures == NULL) {
        perror(argv[1]);
        return 1;
    }

    char line[4096];
    size_t rows = 0;
    int valid = 1;
    while (valid && fgets(line, sizeof(line), fixtures) != NULL) {
        ++rows;
        valid = strchr(line, '\n') != NULL && check_row(line);
    }
    valid = valid && !ferror(fixtures) && rows != 0;
    fclose(fixtures);
    if (!valid) {
        fprintf(stderr, "Kernel fixture failed at line %zu in %s\n", rows, argv[1]);
    }
    return valid ? 0 : 1;
}
