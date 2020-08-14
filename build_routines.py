from cffi import FFI

ffibuilder = FFI()

ffibuilder.cdef(
    "void mandelbrot(long long *inside, double *outside, int width, int height, double offset_x, double offset_y, double center_x, double center_y, double zoom, int exponent, int num_iterations, int inside_cutoff, int outside_cutoff);"
)

ffibuilder.set_source(
    "_routines",
    """
    void eval(long long *inside, double *outside, long long *outside_counter, double x, double y, double cx, double cy, int exponent, int num_iterations, int inside_cutoff, int outside_cutoff) {
        if (inside_cutoff && inside[0] >= inside_cutoff) {
            return;
        }
        if (outside_cutoff && outside_counter[0] >= outside_cutoff) {
            return;
        }
        double r = sqrt(x*x + y*y);
        if (r >= 128) {
            outside_counter[0] += 1;
            double v = num_iterations + log(log(r))/log(exponent + 0.5);
            if (v < outside[0]) {
                outside[0] = v;
            }
            return;
        }
        if (num_iterations == 0) {
            inside[0] += 1;
            return;
        }
        // Square root components
        double sx = sqrt((r + x)*0.5);
        double sy = sqrt((r - x)*0.5);
        if (y < 0) {
            sy = -sy;
        }
        // Closest integer component
        if (exponent == 2) {
            r = x;
            x = x*x - y*y;
            y = 2*r*y;
        } else if (exponent == 3) {
            r = x*x;
            x *= r - 3*y*y;
            y *= 3*r - y*y;
        } else if (exponent == 4) {
            r = x;
            x = x*x - y*y;
            y = 2*r*y;
            r = x;
            x = x*x - y*y;
            y = 2*r*y;
        }
        // z**(n + .5) components
        r = x;
        x = x*sx - y*sy;
        y = r*sy + y*sx;
        eval(inside, outside, outside_counter, cx + x, cy + y, cx, cy, exponent, num_iterations-1, inside_cutoff, outside_cutoff);
        eval(inside, outside, outside_counter, cx - x, cy - y, cx, cy, exponent, num_iterations-1, inside_cutoff, outside_cutoff);
    }

    void mandelbrot(long long *inside, double *outside, int width, int height, double offset_x, double offset_y, double center_x, double center_y, double zoom, int exponent, int num_iterations, int inside_cutoff, int outside_cutoff) {
        zoom = pow(2, -zoom) / height;
        for (size_t i = 0; i < width * height; i++) {
            double x = (i % width) + offset_x;
            double y = (i / width) + offset_y;
            x = (2 * x - width) * zoom + center_x;
            y = (2 * y - height) * zoom + center_y;

            inside[i] = 0;
            outside[i] = INFINITY;
            long long outside_counter = 0;
            eval(inside+i, outside+i, &outside_counter, x, y, x, y, exponent, num_iterations, inside_cutoff, outside_cutoff);
            if (outside[i] == INFINITY) {
                outside[i] = log(log(128))/log(exponent + 0.5);
            }
        }
    }
    """
)

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
