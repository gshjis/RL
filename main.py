"""
Основной скрипт симуляции перевёрнутого маятника с PID-регулятором.
"""

from __future__ import annotations

import numpy as np
from pid import PIDController,terminate_condition
from swing_up_block import SwingUp, SwingUpAndBalance

from packages.controllers.custom import SwingUp
from packages.controllers.PID.optimizers import Genetic_PID_AngleOnly, Zigler_Nikols
from packages.simulation.CO import (
    ControllerConfig,
    NoiseForce,
    ObjectOfControl,
    PlantConfig,
    SensorConfig,
)
from packages.simulation.GUI import PendulumViewer

PLANT_CONFIG = PlantConfig(
    M=1.0,                # масса тележки, кг (реалистично для стенда с ремнём)
    m1=0.23,              # масса маятника, кг (стандарт: 0.2–0.25 кг)
    m2=0.0,
    l1=0.4,               # длина маятника, м (0.3–0.45 м — стандарт)
    l2=0.0,
    L1=0.2,               # ЦМ на середине стержня
    J1=0.0031,            # момент инерции (1/12 * m * l^2 = 1/12*0.23*0.4^2)
    J2=0.0,
    g=-9.81,
    b_c=0.1,              # трение тележки, Н·с/м
    b_1=0.005,             # трение в шарнире, Н·м·с/рад
    b_2=0.0,
    single_pendulum_mode=True,
    backslash_mode=False,
    init_q=np.array([0.0, 0.0, 0.0]),
    init_dq=np.array([0.0, 0.0, 0.0]),
    dt=0.0001,
)

SENSOR_CONFIG = SensorConfig(
    encoder_resolution_1=4096,     # 14 бит — 16384 отсчёта на оборот (~0.022°)
    encoder_resolution_2=4096,
    cart_sensor_resolution=0.0001, # 0.05 мм
    noise_std_q=(0.0005, 0.002, 0.002),   # ~0.03° по углам
    noise_std_dq=(0.005, 0.01, 0.01),     # скорости
)

CONTROLLER_CONFIG = ControllerConfig(
    dt=0.001,
    max_force=24,
    has_velocity_sensors=True,
    filter_cutoff_hz=50.0,
)


if __name__ == "__main__":

    swing_controller = SwingUp(CONTROLLER_CONFIG,150,PLANT_CONFIG)
    pid_controller = PIDController(CONTROLLER_CONFIG, gains=np.array([80.42,0.0,30.71,-10,-15]))
    controller = SwingUpAndBalance(
        CONTROLLER_CONFIG,
        swingup_controller=swing_controller,
        balance_controller=pid_controller
    )
    controller.set_motor_inertia(time_constant=0.1)

    NOISE = NoiseForce(mean=0.00, std=0.03)
    TARGET = np.array([0.0, np.pi, 0.0, 0.0, 0.0, 0.0])

    optimizer = Genetic_PID_AngleOnly()
    # pid_controller.train(
    #     plant_config=PLANT_CONFIG,
    #     sensor_config=SENSOR_CONFIG,
    #     noise=NOISE,
    #     optimizer=optimizer,
    #     target_state=TARGET,
    #     episode_max_time=30.0,
    #     terminate_condition=terminate_condition
    # )

    w = PendulumViewer(
        plant=ObjectOfControl(PLANT_CONFIG),
        sensor_config=SENSOR_CONFIG,
        noise=NOISE,
        target_state=TARGET,
        controller=controller,
    )
    w.use()
