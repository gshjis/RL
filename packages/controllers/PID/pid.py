from __future__ import annotations

from typing import Any, Callable
import cost_functions as cost_f
import numpy as np
from numpy.typing import NDArray

from packages.simulation.CO import (
    Controller,
    ControllerConfig,
    MeasuredState,
    NoiseForce,
    ObjectOfControl,
    PlantConfig,
    SensorBlock,
    SensorConfig,
    clock_cycle
    
)


class PIDController(Controller):
    def __init__(self, config: ControllerConfig) -> None:
        super().__init__(config)
        self.name = "PID"

        if isinstance(config, ControllerConfig):
            gains = config.gains
        self._Kp: float = float(gains[0])
        self._Ki: float = float(gains[1])
        self._Kd: float = float(gains[2])
        self._Kx: float = float(gains[3])
        self._Kdx: float = float(gains[4])

        self._integral: float = 0.0

    # ── Свойства ──────────────────────────────────────────────────────────

    @property
    def gains(self) -> NDArray[np.float64]:
        return np.array([self._Kp, self._Ki, self._Kd, self._Kx, self._Kdx], dtype=np.float64)

    @gains.setter
    def gains(self, value: list[float] | NDArray[np.float64]) -> None:
        self._Kp, self._Ki, self._Kd, self._Kx, self._Kdx = map(float, value)

    # ── Закон управления ──────────────────────────────────────────────────

    def get_action(self, s_clean: MeasuredState, target_state:MeasuredState) -> float:

        error = target_state - s_clean

        self._integral += error.theta1 * self._dt

        F = (
            self._Kp * error.theta1
            + self._Ki * self._integral
            + self._Kd * error.theta1_dot
            + self._Kx * error.x
            + self._Kdx * error.x_dot
        )
        return F

    def reset_angel_integral(self) -> None:
        self._integral = 0.0

    # ── Сброс ─────────────────────────────────────────────────────────────

    def reset(self) -> None:
        super().reset()
        self._integral = 0.0

    # ── Обучение ──────────────────────────────────────────────────────────

    def train(
        self,
        plant_config: PlantConfig,
        sensor_config: SensorConfig,
        noise: NoiseForce,
        target_state: MeasuredState,
        terminate_condition: Callable[[ObjectOfControl], bool] | None = None,
        max_time: float = 10.0,
        *,
        method_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Настройка PID-параметров методом Iterative Feedback Tuning (IFT).

        IFT здесь реализована как итеративное обновление параметров по оценке
        направленного градиента на основе baseline и возмущённого эпизодов.
        Это заменяет ранее стохастический поиск/ES.

        method_options:
        - maxiter (int, default 25)
        - eps (float, default 1e-3)      # величина возмущения
        - alpha (float, default 0.5)     # шаг оптимизации
        - direction ("random"|"unit", default "random")
        - seed (int|None, default None)

        Возвращает словарь с лучшими параметрами и стоимостью.
        """

        opts = method_options or {}
        max_iters = int(opts.get("maxiter", 25))
        eps = float(opts.get("eps", 1e-3))
        alpha = float(opts.get("alpha", 0.5))
        direction = str(opts.get("direction", "random"))
        seed = opts.get("seed", None)

        rng = np.random.default_rng(seed)

        plant = ObjectOfControl(plant_config)
        sensor = SensorBlock(sensor_config)

        x = self.gains.copy()
        best_x = x.copy()
        best_J = float("inf")

        for it in range(max_iters):
            if direction == "unit":
                d = np.ones_like(x)
            else:
                d = rng.normal(size=x.shape)

            # Нормируем направление
            nd = float(np.linalg.norm(d))
            if nd == 0.0:
                d = np.ones_like(x)
                nd = float(np.linalg.norm(d))
            d = d / nd

            # baseline
            self.gains = x
            plant.reset()
            J0, _t0 = self._run_episode(
                plant, sensor, noise, max_time, target_state, terminate_condition
            )

            # perturbed
            x1 = x + eps * d
            self.gains = x1
            plant.reset()
            J1, _t1 = self._run_episode(
                plant, sensor, noise, max_time, target_state, terminate_condition
            )

            grad_dir = (J1 - J0) / eps
            x = x - alpha * grad_dir * d

            # baseline считаем достаточно представительным для best
            if J0 < best_J:
                best_J = float(J0)
                best_x = x.copy()

            print(
                f"[IFT it {it:04d}] J0={J0:10.6f} J1={J1:10.6f} best={best_J:10.6f} "
                f"Kp={x[0]:.4f} Ki={x[1]:.4f} Kd={x[2]:.4f} "
                f"Kx={x[3]:.4f} Kdx={x[4]:.4f}"
            )

            if abs(J1 - J0) < 1e-12:
                break

        self.gains = best_x
        return {"x": best_x, "fun": best_J, "success": True}

    # ── Внутренний метод: прогон эпизода ──────────────────────────────────

    def _run_episode(
        self,
        plant: ObjectOfControl,
        sensor: SensorBlock,
        noise: NoiseForce,
        max_time: float,
        target_state: MeasuredState,
        terminate_condition: Callable[[ObjectOfControl], bool] | None = None,
    ) -> tuple[float, float]:


        dt_control = self._dt

        max_steps = int(max_time / dt_control)
        step = 0

        self.reset()
        F_raw = 0.0
        J = 0.0
        for step in range(max_steps):

            J_val, F_raw = clock_cycle(self, plant, sensor, noise, F_raw, target_state, cost_f.J)
            if terminate_condition is not None and terminate_condition(plant):
                break
            J += J_val

        return (J, step*dt_control)
