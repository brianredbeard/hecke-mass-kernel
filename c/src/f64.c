#include <hecke_mass/f64.h>

double hecke_mass_reciprocal_sum_scalar_f64(const uint32_t *orders, size_t count)
{
    double sum = 0.0;
    for (size_t i = 0; i < count; ++i) {
        if (orders[i] != 0) {
            sum += 1.0 / (double)orders[i];
        }
    }
    return sum;
}

double hecke_mass_weighted_sum_scalar_f64(const double *weights,
                                          const double *samples, size_t count)
{
    double sum = 0.0;
    for (size_t i = 0; i < count; ++i) {
        sum += weights[i] * samples[i];
    }
    return sum;
}

#ifndef HECKE_MASS_ENABLE_RVV
double hecke_mass_reciprocal_sum_ordered_f64(const uint32_t *orders, size_t count)
{
    return hecke_mass_reciprocal_sum_scalar_f64(orders, count);
}

double hecke_mass_reciprocal_sum_unordered_f64(const uint32_t *orders, size_t count)
{
    return hecke_mass_reciprocal_sum_scalar_f64(orders, count);
}

double hecke_mass_weighted_sum_ordered_f64(const double *weights,
                                           const double *samples, size_t count)
{
    return hecke_mass_weighted_sum_scalar_f64(weights, samples, count);
}

double hecke_mass_weighted_sum_unordered_f64(const double *weights,
                                             const double *samples, size_t count)
{
    return hecke_mass_weighted_sum_scalar_f64(weights, samples, count);
}
#endif
