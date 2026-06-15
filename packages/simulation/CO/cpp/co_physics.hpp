#pragma once

struct State3 {
    double x;
    double theta1;
    double theta2;
};

// Equivalent to StateDot but kept separate for clarity.
struct StateDot3 {
    double x_dot;
    double theta1_dot;
    double theta2_dot;
};

struct PlantParams {
    double M;
    double m1;
    double m2;
    double l1;
    double l2;
    double L1;
    double L2;
    double J1;
    double J2;
    double g;
    double b_c;
    double b_1;
    double b_2;
};

struct NoiseForceCPP {
    double mean;
    double std;
};

double sample_noise_force(const NoiseForceCPP& n);

StateDot3 compute_ddq(const State3& q, const StateDot3& dq, double F_total,
                       const PlantParams& p, bool single_mode);

// One RK4 micro-step.
void rk4_step(State3& q, StateDot3& dq, double F_total, double dt,
              const PlantParams& p, bool single_mode);
