// Evaluate the organisers' CEC 2022 C code on points read from a file.
// usage: driver FUNC DIM POINTS_FILE   (file: count, then count*DIM numbers)
// Run from the folder that holds input_data/.
#include <cstdio>
#include <cstdlib>
double *OShift, *M, *y, *z, *x_bound;
int ini_flag = 0, n_flag, func_flag, *SS;
void cec22_test_func(double *, double *, int, int, int);
int main(int argc, char **argv) {
  if (argc != 4) return 2;
  int func = atoi(argv[1]), nx = atoi(argv[2]);
  FILE *in = fopen(argv[3], "r");
  if (!in) return 3;
  int m;
  if (fscanf(in, "%d", &m) != 1) return 4;
  double *x = (double *)malloc(sizeof(double) * m * nx);
  for (int i = 0; i < m * nx; i++) if (fscanf(in, "%lf", &x[i]) != 1) return 5;
  fclose(in);
  double *f = (double *)malloc(sizeof(double) * m);
  for (int i = 0; i < m; i++) cec22_test_func(&x[i * nx], &f[i], nx, 1, func);
  for (int i = 0; i < m; i++) printf("%.17g\n", f[i]);
  return 0;
}
