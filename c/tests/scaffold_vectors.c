#include <hecke_mass/scaffold.h>

#include <inttypes.h>
#include <stdio.h>
#include <string.h>

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

    enum { capacity = 128 };
    uint32_t inputs[capacity], expected[capacity], outputs[capacity];
    uint32_t input, output;
    size_t count = 0;
    int fields;
    while ((fields = fscanf(fixtures, "%" SCNu32 ",%" SCNu32, &input, &output)) == 2) {
        if (count == capacity) {
            break;
        }
        inputs[count] = input;
        expected[count] = output;
        ++count;
    }
    int valid = fields == EOF && !ferror(fixtures) && count > 0;
    fclose(fixtures);
    if (!valid) {
        fprintf(stderr, "Invalid scaffold fixture file: %s\n", argv[1]);
        return 1;
    }

    hecke_mass_scaffold_probe(NULL, NULL, 0);
    for (size_t length = 1; length <= count; ++length) {
        size_t bytes = length * sizeof(uint32_t);
        memcpy(outputs, inputs, bytes);
        hecke_mass_scaffold_probe(inputs, outputs, length);
        if (memcmp(expected, outputs, bytes) != 0) {
            fprintf(stderr, "Scaffold probe failed for length %zu\n", length);
            return 1;
        }
        memcpy(outputs, inputs, bytes);
        hecke_mass_scaffold_probe(outputs, outputs, length);
        if (memcmp(expected, outputs, bytes) != 0) {
            fprintf(stderr, "In-place scaffold probe failed for length %zu\n", length);
            return 1;
        }
    }
    return 0;
}
