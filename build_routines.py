from cffi import FFI

ffibuilder = FFI()

ffibuilder.cdef(
    "void mandelbrot(long long *inside, double *outside, int width, int height, double offset_x, double offset_y, double center_x, double center_y, double zoom, int exponent, int num_iterations, int inside_cutoff, int clip_outside);"
    "void mandelbrot_generic(double *in_x_out_inside, double *in_y_out_outside, int num_samples, int numerator, int denominator, int num_iterations, int inside_cutoff, double outside_offset, int clip_outside, double julia_cx, double julia_cy, int julia);"
    "void buddhabrot(double *samples, double *c_samples, size_t num_samples, unsigned long long *counts, int width, int height, double x0, double y0, double dx00, double dx01, double dx10, double dx11, int numerator, int denominator, int num_iterations, int min_iteration, double bailout, unsigned int seed);"
)

ffibuilder.set_source(
    "_routines",
    """
    /* Public domain code for JKISS RNG */
    // http://www0.cs.ucl.ac.uk/staff/d.jones/GoodPracticeRNG.pdf
    typedef struct jkiss32
    {
        unsigned int x, y, z, c;
    } jkiss32;

    void jkiss32_seed(jkiss32 *gen, unsigned int seed) {
        gen->x = seed;
        gen->y = seed*seed + 17;
        if (gen->y == 0) {
            gen->y = 7;
        }
        gen->z = gen->y * seed + 27;
        gen->c = (gen->z * seed + 237) % 698769068 + 1;
    }

    unsigned int jkiss32_step(jkiss32 *gen) {
        unsigned long long t;
        gen->x = 314527869 * gen->x + 1234567;
        gen->y ^= gen->y << 5; gen->y ^= gen->y >> 7; gen->y ^= gen->y << 22;
        t = 4294584393ULL * gen->z + gen->c;
        gen->c = t >> 32;
        gen->z = t;
        return gen->x + gen->y + gen->z;
    }
    /* End code for JKISS RNG */

    void eval(long long *inside, double *outside, double x, double y, double cx, double cy, int exponent, int num_iterations, int inside_cutoff, int clip_outside, double i_log_exponent) {
        if (inside_cutoff && inside[0] >= inside_cutoff) {
            return;
        }
        double x2 = x*x;
        double y2 = y*y;
        double r = sqrt(x2 + y2);
        if (r >= 128) {
            if (!clip_outside || inside[0] == 0) {
                double v = num_iterations + log(log(r))*i_log_exponent;
                if (v < outside[0]) {
                    outside[0] = v;
                }
            }
            return;
        }
        if (num_iterations == 0) {
            inside[0] += 1;
            return;
        }
        // Square root components
        double sx = sqrt((r + x)*0.5);
        double sy = copysign(sqrt((r - x)*0.5), y);
        // Closest integer component
        if (exponent == 2) {
            y *= 2*x;
            x = x2 - y2;
        } else if (exponent == 3) {
            x *= x2 - 3*y2;
            y *= 3*x2 - y2;
        } else if (exponent == 4) {
            y = 2*x*y;
            x = x2 - y2;
            y2 = y*y;
            y = 2*x*y;
            x = x*x - y2;
        }
        // z**(n + .5) components
        r = x;
        x = x*sx - y*sy;
        y = r*sy + y*sx;
        eval(inside, outside, cx + x, cy + y, cx, cy, exponent, num_iterations-1, inside_cutoff, clip_outside, i_log_exponent);
        eval(inside, outside, cx - x, cy - y, cx, cy, exponent, num_iterations-1, inside_cutoff, clip_outside, i_log_exponent);
    }

    void mandelbrot(long long *inside, double *outside, int width, int height, double offset_x, double offset_y, double center_x, double center_y, double zoom, int exponent, int num_iterations, int inside_cutoff, int clip_outside) {
        zoom = pow(2, -zoom) / height;
        for (size_t i = 0; i < width * height; i++) {
            double x = (i % width) + offset_x;
            double y = (i / width) + offset_y;
            x = (2 * x - width) * zoom + center_x;
            y = (2 * y - height) * zoom + center_y;

            inside[i] = 0;
            outside[i] = INFINITY;
            double i_log_exponent = 1.0/log(exponent + 0.5);
            eval(inside+i, outside+i, x, y, x, y, exponent, num_iterations, inside_cutoff, clip_outside, i_log_exponent);
            // log(log(128)) == 1.5793972284736488
            outside[i] -= 1.5793972284736488*i_log_exponent;
            if (outside[i] == INFINITY || (clip_outside && inside[i] > 0)) {
                outside[i] = 0;
            }
        }
    }

    void eval_generic(double *inside, double *outside, double *roots_of_unity, double x, double y, double cx, double cy, double exponent, int denominator, int num_iterations, int inside_cutoff, double outside_offset, int clip_outside) {
        if (inside_cutoff && inside[0] >= inside_cutoff) {
            return;
        }
        double r = x*x + y*y;
        if (r >= 128*128) {
            if (!clip_outside || inside[0] == 0) {
                double v = fabs(num_iterations + log(log(r)*0.5)/log(exponent) + outside_offset);
                if (v < outside[0]) {
                    outside[0] = v;
                }
            }
            return;
        }
        if (num_iterations == 0) {
            inside[0] += 1;
            return;
        }
        double theta = atan2(y, x)*exponent;
        r = pow(r, exponent*0.5);
        x = cos(theta) * r;
        y = sin(theta) * r;
        for (int i = 0; i < denominator; ++i) {
            eval_generic(
                inside, outside, roots_of_unity,
                x*roots_of_unity[2*i] + y*roots_of_unity[2*i+1] + cx,
                y*roots_of_unity[2*i] - x*roots_of_unity[2*i+1] + cy,
                cx, cy, exponent, denominator, num_iterations-1, inside_cutoff, outside_offset, clip_outside
            );
        }
    }

    void eval_nonescaping(double *max_r2, double *phase, double *roots_of_unity, double x, double y, double cx, double cy, double exponent, int denominator, int num_iterations) {
        double r = x*x + y*y;
        double theta = atan2(y, x);
        if ((exponent < 0 && r >= max_r2[0]) || (exponent >= 0 && r <= max_r2[0])) {
            max_r2[0] = r;
            phase[0] = theta;
        }
        if (num_iterations == 0) {
            return;
        }
        theta *= exponent;
        r = pow(r, exponent*0.5);
        x = cos(theta) * r;
        y = sin(theta) * r;
        for (int i = 0; i < denominator; ++i) {
            eval_nonescaping(
                max_r2, phase, roots_of_unity,
                x*roots_of_unity[2*i] + y*roots_of_unity[2*i+1] + cx,
                y*roots_of_unity[2*i] - x*roots_of_unity[2*i+1] + cy,
                cx, cy, exponent, denominator, num_iterations-1
            );
        }
    }

    void mandelbrot_generic(double *in_x_out_inside, double *in_y_out_outside, int num_samples, int numerator, int denominator, int num_iterations, int inside_cutoff, double outside_offset, int clip_outside, double julia_cx, double julia_cy, int julia) {
        if (denominator < 0) {
            denominator = -denominator;
            numerator = -numerator;
        }
        double *roots_of_unity = malloc(2*denominator*sizeof(double));
        for (int i = 0; i < denominator; ++i) {
            roots_of_unity[2*i+0] = cos(i*2*M_PI/(double)denominator);
            roots_of_unity[2*i+1] = sin(i*2*M_PI/(double)denominator);
        }
        double exponent = numerator / (double) denominator;
        double outside_placeholder = fabs(outside_offset);
        outside_offset -= log(log(128))/log(exponent);
        for (size_t i = 0; i < num_samples; i++) {
            double x = in_x_out_inside[i];
            double y = in_y_out_outside[i];
            double cx = x;
            double cy = y;
            if (julia) {
                cx = julia_cx;
                cy = julia_cy;
            }
            if (exponent >= 1) {
                in_x_out_inside[i] = 0;
                in_y_out_outside[i] = INFINITY;
                eval_generic(in_x_out_inside+i, in_y_out_outside+i, roots_of_unity, x, y, cx, cy, exponent, denominator, num_iterations, inside_cutoff, outside_offset, clip_outside);
                if (in_y_out_outside[i] == INFINITY || (clip_outside && in_x_out_inside[i] > 0)) {
                    in_y_out_outside[i] = outside_placeholder;
                }
            } else {
                // Radius^2
                if (exponent < 0) {
                    in_x_out_inside[i] = 0;
                } else {
                    in_x_out_inside[i] = INFINITY;
                }
                eval_nonescaping(in_x_out_inside+i, in_y_out_outside+i, roots_of_unity, x, y, cx, cy, exponent, denominator, num_iterations);
                in_x_out_inside[i] = sqrt(in_x_out_inside[i]);
            }
        }
        free(roots_of_unity);
    }

    void eval_buddhabrot(jkiss32 *gen, double *roots_of_unity, double x, double y, double cx, double cy, double exponent, int denominator, int num_iterations, int min_iteration, double bailout, unsigned long long *counts, int width, int height, double x0, double y0, double dx00, double dx01, double dx10, double dx11) {
        if (min_iteration <= 0) {
            int index_x = x0 + x*dx00 + y*dx01;
            int index_y = y0 + x*dx10 + y*dx11;
            if (index_x >= 0 && index_x < width && index_y >= 0 && index_y < height) {
                __sync_add_and_fetch(counts + index_x + index_y*width, 1);
            }
        }
        if (num_iterations == 0) {
            return;
        }
        double r = x*x + y*y;
        if (r > bailout) {
            return;
        }
        double theta = atan2(y, x) * exponent;
        r = pow(r, exponent*0.5);
        x = cos(theta) * r;
        y = sin(theta) * r;

        int i = jkiss32_step(gen) % denominator;
        eval_buddhabrot(
            gen, roots_of_unity,
            x*roots_of_unity[2*i] + y*roots_of_unity[2*i+1] + cx,
            y*roots_of_unity[2*i] - x*roots_of_unity[2*i+1] + cy,
            cx, cy, exponent, denominator, num_iterations-1, min_iteration-1, bailout,
            counts, width, height, x0, y0, dx00, dx01, dx10, dx11
        );
    }

    void buddhabrot(double *samples, double *c_samples, size_t num_samples, unsigned long long *counts, int width, int height, double x0, double y0, double dx00, double dx01, double dx10, double dx11, int numerator, int denominator, int num_iterations, int min_iteration, double bailout, unsigned int seed) {
        jkiss32 gen;
        jkiss32_seed(&gen, seed);
        if (denominator < 0) {
            denominator = -denominator;
            numerator = -numerator;
        }
        double *roots_of_unity = malloc(2*denominator*sizeof(double));
        for (int i = 0; i < denominator; ++i) {
            roots_of_unity[2*i+0] = cos(i*2*M_PI/(double)denominator);
            roots_of_unity[2*i+1] = sin(i*2*M_PI/(double)denominator);
        }
        double exponent = numerator / (double) denominator;
        for (size_t i=0; i < num_samples; ++i) {
            double x = samples[2*i];
            double y = samples[2*i + 1];
            double cx = c_samples[2*i];
            double cy = c_samples[2*i + 1];
            eval_buddhabrot(&gen, roots_of_unity, x, y, cx, cy, exponent, denominator, num_iterations, min_iteration, bailout, counts, width, height, x0, y0, dx00, dx01, dx10, dx11);
        }
        free(roots_of_unity);
    }

    """
)

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
