from __future__ import annotations

from typing import Any, Callable

import numpy as np

from packages.simulation.CO import (
    Controller,
    ControllerConfig,
    MeasuredState,
    NoiseForce,
    ObjectOfControl,
    PlantConfig,
    SensorBlock,
    SensorConfig,
    clock_cycle,
)

import packages.controllers.PID.cost_functions as cost_f


class ReinforceController(Controller):
    """Наследник базового [`Controller`] с каркасом обучения в стиле REINFORCE.

    Реальная реализация REINFORCE требует policy distribution и log-prob.
    Здесь для совместимости с текущим проектом оставлен end-to-end каркас:
    - `get_action()` реализован как линейная policy `u = w · s_clean`.
    - `train()` обновляет веса по стоимости эпизода (мутационный
      градиентоподобный шаг).
    """

    def __init__(self, config: ControllerConfig) -> None:
        super().__init__(config)
        self.name = "REINFORCE"

        # s_clean: (x, theta1, theta2, x_dot, theta1_dot, theta2_dot)
        self._w: np.ndarray = np.zeros(6, dtype=np.float64)

    @property
    def weights(self) -> np.ndarray:
        return self._w

    @weights.setter
    def weights(self, value: np.ndarray | list[float]) -> None:
        arr = np.asarray(value, dtype=np.float64)
        if arr.shape != (6,):
            raise ValueError("weights must have shape (6,)")
        self._w = arr

    def get_action(self, s_clean: MeasuredState, target_state: MeasuredState) -> float:
        s = np.array(
            [
                s_clean.x,
                s_clean.theta1,
                s_clean.theta2,
                s_clean.x_dot,
                s_clean.theta1_dot,
                s_clean.theta2_dot,
            ],
            dtype=np.float64,
        )
        return float(self._w.dot(s))

    def train(
        self,
        plant_config: PlantConfig,
        sensor_config: SensorConfig,
        noise: NoiseForce,
        *,
        max_time: float = 10.0,
        method_options: dict[str, Any] | None = None,
        target_state: MeasuredState,
        terminate_condition: Callable[[ObjectOfControl], bool] | None = None,
    ) -> dict[str, Any]:
        """Обучение каркаса REINFORCE.

        method_options:
        - episodes (int, default 8)
        - lr (float, default 1e-2)
        - mut_scale (float, default 0.1)
        """

        opts = method_options or {}
        episodes = int(opts.get("episodes", 8))
        lr = float(opts.get("lr", 1e-2))
        mut_scale = float(opts.get("mut_scale", 0.1))

        best_w = self._w.copy()
        best_J = float("inf")

        rng = np.random.default_rng(opts.get("seed", None))

        for ep in range(episodes):
            w_pert = self._w + rng.normal(scale=mut_scale, size=self._w.shape)
            self._w = w_pert

            plant = ObjectOfControl(plant_config)
            sensor = SensorBlock(sensor_config)

            F_raw = 0.0
            J_total = 0.0

            max_steps = int(max_time / self._dt)
            self.reset()
            for _ in range(max_steps):
                J_val, F_raw = clock_cycle(
                    self,
                    plant,
                    sensor,
                    noise,
                    F_raw,
                    target_state,
                    lambda measured, targ: cost_f.J(targ, measured),
                )
                J_total += float(J_val)
                if terminate_condition is not None and terminate_condition(plant):
                    break

            if J_total < best_J:
                best_J = float(J_total)
                best_w = self._w.copy()

            # “шаг” к лучшему
            self._w = self._w + lr * (best_w - self._w)

        self._w = best_w
        return {"x": best_w, "fun": best_J, "success": True}
