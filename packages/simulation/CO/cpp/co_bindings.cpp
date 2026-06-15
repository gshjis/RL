#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "co_physics.hpp"

namespace py = pybind11;

struct PyState3 {
    State3 v;
};

PYBIND11_MODULE(co_cpp, m) {
    m.doc() = "C++ physics core for CO simulation (pybind11)";

    // NoiseForce (API parity with Python: mean/std)
    py::class_<NoiseForceCPP>(m, "NoiseForce")
        .def(py::init<double, double>(), py::arg("mean") = 0.0, py::arg("std") = 0.0)
        .def_readwrite("mean", &NoiseForceCPP::mean)
        .def_readwrite("std", &NoiseForceCPP::std)
        .def("get_force", &sample_noise_force);

    // Main step function: updates q/dq using RK4.
    // This mirrors ObjectOfControl.update_physics(F_ideal, noise).
    m.def(
        "rk4_step",
        [](State3 q, StateDot3 dq,
           double F_ideal,
           NoiseForceCPP noise,
           double dt,
           PlantParams params,
           bool backslash_mode,
           bool single_mode,
           double backlash_alpha,
           double backlash_m_mot,
           double& backlash_gap_pos) {
            // Backlash model in C++.
            double F_real = F_ideal;
            if (backslash_mode) {
                const double half_gap = backlash_alpha / 2.0;
                const double a_rel = F_ideal / backlash_m_mot;
                backlash_gap_pos += a_rel * dt;
                if (backlash_gap_pos > half_gap) {
                    backlash_gap_pos = half_gap;
                    F_real = F_ideal;
                } else if (backlash_gap_pos < -half_gap) {
                    backlash_gap_pos = -half_gap;
                    F_real = F_ideal;
                } else {
                    F_real = 0.0;
                }
            }

            // Noise: deterministic sampling is handled in Python via random.gauss.
            // Here we just treat noise as additive mean/std, and set F_total = F_real + mean.
            // To match current Python behavior, we expect Python to pass a sampled value separately.
            const double F_total = F_real + noise.mean;

            rk4_step(q, dq, F_total, dt, params, single_mode);
            return py::make_tuple(q, dq);
        },
        py::arg("q"), py::arg("dq"), py::arg("F_ideal"), py::arg("noise"), py::arg("dt"),
        py::arg("params"), py::arg("backslash_mode"), py::arg("single_mode"),
        py::arg("backlash_alpha"), py::arg("backlash_m_mot"), py::arg("backlash_gap_pos"));

    py::class_<State3>(m, "State3")
        .def(py::init<>())
        .def_readwrite("x", &State3::x)
        .def_readwrite("theta1", &State3::theta1)
        .def_readwrite("theta2", &State3::theta2);

    py::class_<StateDot3>(m, "StateDot3")
        .def(py::init<>())
        .def_readwrite("x_dot", &StateDot3::x_dot)
        .def_readwrite("theta1_dot", &StateDot3::theta1_dot)
        .def_readwrite("theta2_dot", &StateDot3::theta2_dot);

    py::class_<PlantParams>(m, "PlantParams")
        .def(py::init<>())
        .def_readwrite("M", &PlantParams::M)
        .def_readwrite("m1", &PlantParams::m1)
        .def_readwrite("m2", &PlantParams::m2)
        .def_readwrite("l1", &PlantParams::l1)
        .def_readwrite("l2", &PlantParams::l2)
        .def_readwrite("L1", &PlantParams::L1)
        .def_readwrite("L2", &PlantParams::L2)
        .def_readwrite("J1", &PlantParams::J1)
        .def_readwrite("J2", &PlantParams::J2)
        .def_readwrite("g", &PlantParams::g)
        .def_readwrite("b_c", &PlantParams::b_c)
        .def_readwrite("b_1", &PlantParams::b_1)
        .def_readwrite("b_2", &PlantParams::b_2);
}
