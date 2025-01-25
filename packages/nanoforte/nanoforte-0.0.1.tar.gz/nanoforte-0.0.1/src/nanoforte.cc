#include <nanobind/nanobind.h>

namespace nb = nanobind;
using namespace nb::literals;

int add(int a, int b) { return a + b; }

NB_MODULE(libnanoforte, m) {
  m.def("add", &add, "a"_a, "b"_a, "This is a test function.");

  m.attr("the_answer") = 42;
}