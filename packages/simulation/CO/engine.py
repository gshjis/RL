class MotorInertia:
    """
    Модель инерционности двигателя (апериодическое звено первого порядка).

    Parameters
    ----------
    time_constant : float
        Постоянная времени двигателя (с). Определяет, как быстро реальная сила
        достигает целевой.
    """

    def __init__(self, time_constant: float) -> None:
        self._tau = float(time_constant)
        self._current_force = 0.0

    @property
    def current_force(self) -> float:
        """Текущее реальное усилие (Н)."""
        return self._current_force

    def update(self, target_force: float, dt: float) -> float:
        """
        Обновить текущее усилие с учетом инерции.

        Parameters
        ----------
        target_force : float
            Целевое управляющее усилие (Н).
        dt : float
            Шаг интегрирования (с).

        Returns
        -------
        float
            Реальное усилие на тележке (Н).
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
        """Сбросить состояние инерции."""
        self._current_force = 0.0
