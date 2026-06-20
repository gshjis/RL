class MotorInertia:
    """
    Модель инерционности двигателя (апериодическое звено первого порядка).

    Реализует дискретную аппроксимацию передаточной функции
    :math:`F_{out}(s) / F_{target}(s) = 1 / (\\tau s + 1)`:

    .. math::

        F_{k+1} = F_k + (F_{target} - F_k) \\cdot \\frac{dt}{\\tau}

    Parameters
    ----------
    time_constant : float
        Постоянная времени двигателя (с). Определяет, как быстро реальная сила
        достигает целевой. Если ``<= 0`` — инерция отключена (мгновенный отклик).

    Notes
    -----
    Модель **не** учитывает:
        - Ограничение по току (насыщение производной)
        - Нелинейности типа сухого трения
        - Запаздывание (dead time)

    Optimization potential:
        - Операцию деления ``dt / tau`` можно предвычислить в ``__init__``
          (сейчас вычисляется на каждом ``update()``, но ``dt`` фиксирован).
        - В цикле симуляции можно объединить с ``compute_control``,
          чтобы избежать лишнего вызова метода.
    """

    def __init__(self, time_constant: float) -> None:
        self._tau: float = float(time_constant)
        self._current_force: float = 0.0

    @property
    def current_force(self) -> float:
        """Текущее реальное усилие на тележке (Н)."""
        return self._current_force

    def update(self, target_force: float, dt: float) -> float:
        """
        Обновить текущее усилие с учётом инерции.

        Parameters
        ----------
        target_force : float
            Целевое управляющее усилие (Н).
        dt : float
            Шаг интегрирования (с).

        Returns
        -------
        float
            Реальное усилие на тележке после учёта инерции (Н).

        Examples
        --------
        >>> motor = MotorInertia(time_constant=0.05)
        >>> motor.update(30.0, 0.005)  # первый шаг от 0
        3.0
        """
        if self._tau > 0:
            # Дискретная аппроксимация апериодического звена:
            # F_new = F_old + (F_target - F_old) * (dt / tau)
            self._current_force += (target_force - self._current_force) * (dt / self._tau)
        else:
            # Если tau <= 0, инерция отсутствует (мгновенный отклик)
            self._current_force = target_force
        return self._current_force

    def reset(self) -> None:
        """Сбросить состояние инерции (обнулить текущее усилие)."""
        self._current_force = 0.0
