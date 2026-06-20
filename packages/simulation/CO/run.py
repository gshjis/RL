from packages.simulation.CO.datatypes import NoiseForce
from packages.simulation.CO.pendulum import ObjectOfControl
from packages.simulation.CO.sensor import SensorBlock
from packages.simulation.CO.controller import Controller
from typing import Callable
import numpy as np


def clock_cycle(
    controller: Controller,
    plant: ObjectOfControl,
    sensor: SensorBlock,
    noise: NoiseForce,
    old_F: float,
    target_state: np.ndarray,
    J: Callable[[np.ndarray, np.ndarray], float],
) -> tuple[float, float]:
    """
    Выполнить один такт управления (control-tick) и вернуть значение
    целевой функции и новую управляющую силу.

    Логика включает **искусственную задержку** вычисления управляющего
    воздействия: управление пересчитывается только после того, как физика
    отработала ~20–50% от длительности control-tick, используя предыдущее
    значение силы. Это имитирует вычислительную задержку реального УУ.

    Алгоритм:

    1. Вычислить число микрошагов физики в одном control-tick.
    2. Случайная доля ``freeze_ratio ∈ [0.2, 0.5]`` — фаза "заморозки":
       физика работает с предыдущим ``old_F``.
    3. Получить телеметрию и пересчитать управление через
       ``controller.compute_control()``.
    4. Оставшаяся часть такта: физика работает с новым ``F_raw``.
    5. Вернуть ``J(target_state, measured)`` и ``F_raw``.

    Parameters
    ----------
    controller : Controller
        Блок вычисления управления (должен реализовывать ``get_action``).
    plant : ObjectOfControl
        Объект управления (физическая модель).
    sensor : SensorBlock
        Блок получения телеметрии (квантование + шум).
    noise : NoiseForce
        Мгновенное значение силы внешнего возмущения.
    old_F : float
        Сила (Н), применявшаяся на предыдущем такте.
    target_state : np.ndarray
        Целевой вектор состояния ``(x, θ₁, θ₂, ẋ, θ̇₁, θ̇₂)``.
    J : Callable[[np.ndarray, np.ndarray], float]
        Функция стоимости/награды: ``J(target_state, measured) -> float``.
        Вызывается **после** полного такта управления.

    Returns
    -------
    tuple[float, float]
        ``(J_value, F_raw)``:
        - ``J_value`` — значение целевой функции на последней телеметрии
        - ``F_raw`` — новая управляющая сила (Н)

    Notes
    -----
    **Зачем нужна задержка?** В реальном контроллере есть вычислительная
    задержка между съёмом показаний и выдачей управления. ``freeze_ratio``
    имитирует эту задержку со случайной вариацией (±15% от номинала).

    Optimization potential:
        - ``freeze_ratio`` генерируется через ``np.random.random()`` на
          каждом такте; если задержка не критична, можно использовать
          фиксированное значение (например, 0.33) для воспроизводимости.
        - Два вызова ``plant.update_physics`` (до и после пересчёта
          управления) можно объединить в один с сохранением состояния
          в момент замера.
        - Вызов ``plant.q`` и ``plant.dq`` внутри ``sensor.get_telemetry``
          создаёт копии массивов (см. ``ObjectOfControl``).
    """

    dt_control: float = controller._dt
    dt_physics: float = plant._dt

    # Общее число шагов физики в одном тике управления.
    steps_per_control: int = int(dt_control / dt_physics)
    # Доля времени, в течение которой управление не пересчитывается (задержка).
    freeze_ratio: float = 0.3 * np.random.random() + 0.2
    count_time: int = int(steps_per_control * freeze_ratio)
    remaining_steps: int = steps_per_control - count_time

    F_raw: float = float(old_F)
    measured: np.ndarray = sensor.get_telemetry(plant.q, plant.dq)

    # Фаза задержки: физика работает, используя предыдущее воздействие.
    for _ in range(count_time):
        plant.update_physics(F_raw, noise)

    # Пересчёт управления.
    F_raw = controller.compute_control(measured, target_state)

    # Фаза применения нового управления до конца control-tick.
    for _ in range(remaining_steps):
        plant.update_physics(F_raw, noise)

    measured = sensor.get_telemetry(plant.q, plant.dq)
    return J(target_state, measured), F_raw
