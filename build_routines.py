from cffi import FFI

ffibuilder = FFI()

ffibuilder.cdef(
    "void mandelbrot(long long *inside, double *outside, int width, int height, double offset_x, double offset_y, double center_x, double center_y, double zoom, int num_iterations);"
)

ffibuilder.set_source(
    "_routines",
    """
    void eval(long long *inside, double *outside, double x, double y, double cx, double cy, int num_iterations) {
        double r = sqrt(x*x + y*y);
        if (r >= 128) {
            double v = num_iterations + log(log(r))/log(2.5);
            if (v < outside[0]) {
                outside[0] = v;
            }
            return;
        }
        if (num_iterations == 0) {
            inside[0] += 1;
            outside[0] = 0;
            return;
        }
        // Square root components
        double sx = sqrt((r + x)*0.5);
        double sy = sqrt((r - x)*0.5);
        if (y < 0) {
            sy = -sy;
        }
        // Square components
        r = x;
        x = x*x - y*y;
        y = 2*r*y;
        // z**2.5 components
        r = x;
        x = x*sx - y*sy;
        y = r*sy + y*sx;
        eval(inside, outside, cx + x, cy + y, cx, cy, num_iterations-1);
        eval(inside, outside, cx - x, cy - y, cx, cy, num_iterations-1);
    }

    void eval_classic(long long *inside, double *outside, double x, double y, double cx, double cy, int num_iterations) {
        if (x*x + y*y > 128*128) {
            outside[0] = num_iterations;
            return;
        }
        if (num_iterations == 0) {
            inside[0] = 1;
            return;
        }
        eval_classic(inside, outside, x*x - y*y + cx, 2*x*y + cy, cx, cy, num_iterations-1);
    }

    void mandelbrot(long long *inside, double *outside, int width, int height, double offset_x, double offset_y, double center_x, double center_y, double zoom, int num_iterations) {
        zoom = pow(2, -zoom) / height;
        for (size_t i = 0; i < width * height; i++) {
            double x = (i % width) + offset_x;
            double y = (i / width) + offset_y;
            x = (2 * x - width) * zoom + center_x;
            y = (2 * y - height) * zoom + center_y;

            inside[i] = 0;
            outside[i] = num_iterations+1;
            eval(inside+i, outside+i, x, y, x, y, num_iterations);
        }
    }
    """
)

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
