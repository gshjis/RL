"""Профилирование метода train у PID-контроллера.

Запуск:
    poetry run python profiling/profile_pid_train.py

Результаты:
    - profiling_outputs/*.pstats (cProfile)
    - profiling_outputs/*.json (line_profiler при наличии)

Важно:
Этот скрипт не пытается воспроизвести обучение до идеального результата.
Он делает несколько итераций train, чтобы увидеть узкие места.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import time
import cProfile
import pstats

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from packages.controllers.PID import PIDController  # noqa: E402
from packages.simulation.CO.datatypes import (  # noqa: E402
    ControllerConfig,
    PlantConfig,
    SensorConfig,
    NoiseForce,
    MeasuredState,
)



def main() -> None:
    out_dir = Path("profiling_outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Берём конфигурации “по умолчанию”, чтобы скрипт работал сразу.
    controller_cfg = ControllerConfig(dt=0.005, gains=[10.0, 1.0, 2.0, 1.0, 2.0])
    pid = PIDController(controller_cfg)

    plant_cfg = PlantConfig(dt=0.0005)
    sensor_cfg = SensorConfig()
    noise = NoiseForce(mean=0.0, std=0.0)

    target = MeasuredState(
        x=0.0,
        theta1=3.141592653589793,
        theta2=0.0,
        x_dot=0.0,
        theta1_dot=0.0,
        theta2_dot=0.0,
    )

    # Ограничиваем размер задачи, чтобы профиль было реально получить.
    method_options = {
        "maxiter": 3,
        "pop_size": 8,
        "sigma": 0.5,
    }

    # Общий профиль CPU времени.
    profiler = cProfile.Profile()
    t0 = time.perf_counter()
    profiler.enable()
    try:
        result = pid.train(
            plant_config=plant_cfg,
            sensor_config=sensor_cfg,
            noise=noise,
            method_options=method_options,
            target_state=target,
            terminate_condition=None,
            max_time=1
        )
    finally:
        profiler.disable()
    elapsed = time.perf_counter() - t0

    print("Train finished in", elapsed, "sec")
    print("Result fun=", result.get("fun"))

    pstats_path = out_dir / f"pid_train_{int(t0)}.pstats"
    profiler.dump_stats(str(pstats_path))

    # Топ по времени
    ps = pstats.Stats(str(pstats_path))
    ps.strip_dirs().sort_stats("cumtime").print_stats(30)


if __name__ == "__main__":
    main()
