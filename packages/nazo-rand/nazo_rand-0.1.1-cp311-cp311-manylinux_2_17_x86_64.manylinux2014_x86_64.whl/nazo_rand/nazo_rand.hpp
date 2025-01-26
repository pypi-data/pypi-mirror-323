#pragma once
#include <algorithm>
#include <cstdint>
#include <limits>
#include <random>
#include <iostream>
#include <fstream>
#include <vector>
namespace Storm
{
    using Integer = int64_t;

    inline std::mt19937_64 &get_generator()
    {
        static std::mt19937_64 generator{std::random_device{}()};
        return generator;
    }

    inline void seed(uint64_t seed)
    {
        get_generator().seed(seed);
    }

    inline Integer uniform_int_variate(Integer a, Integer b)
    {
        std::uniform_int_distribution<Integer> distribution{std::min(a, b), std::max(b, a)};
        return distribution(get_generator());
    }

    inline Integer uniform_int_variate_noargs()
    {
        return uniform_int_variate(std::numeric_limits<Integer>::min(), std::numeric_limits<Integer>::max());
    }

    inline Integer random_below(Integer number)
    {
        return uniform_int_variate(0, number - 1);
    }

    inline Integer random_range(Integer start, Integer stop, Integer step)
    {
        if (start == stop || step == 0)
            return start;

        Integer width = std::abs(stop - start) - 1;
        Integer step_size = std::abs(step);
        Integer num_steps = (width + step_size) / step_size;
        Integer random_step = random_below(num_steps);

        if (step > 0)
        {
            Integer pivot = std::min(start, stop);
            return pivot + step_size * random_step;
        }
        else
        {
            Integer pivot = std::max(start, stop);
            return pivot - step_size * random_step;
        }
    }

    inline double uniform_real_variate(double a, double b)
    {
        std::uniform_real_distribution<double> distribution{a, b};
        return distribution(get_generator());
    }

    inline double uniform_real_variate_noargs()
    {
        std::uniform_real_distribution<double> distribution{0.0, 1.0};
        return distribution(get_generator());
    }

}
