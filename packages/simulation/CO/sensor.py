import numpy as np
from packages.simulation.CO.datatypes import SensorConfig



class SensorBlock:
    """
    Имитация измерительной подсистемы аппаратного стенда.

    Вносит в чистые координаты ОУ искажения, характерные для реальных
    физических приборов: дискретность цифровых энкодеров по уровню
    (квантование) и высокочастотные наводки в цепях (белый измерительный шум).
    """

    # ──────────────────────────────────────────────────────────────────────
    # Конструктор
    # ──────────────────────────────────────────────────────────────────────

    def __init__(self, config: SensorConfig) -> None:
        """
        Parameters
        ----------
        config : SensorConfig
            Типизированная конфигурация датчиков и шумов.
        """
        self._encoder_res_1: int = config.encoder_resolution_1
        self._encoder_res_2: int = config.encoder_resolution_2
        self._cart_res: float = config.cart_sensor_resolution

        self._angle_step_1: float = 2.0 * np.pi / self._encoder_res_1
        self._angle_step_2: float = 2.0 * np.pi / self._encoder_res_2
        self._cart_step: float = self._cart_res
        self._rng = np.random.default_rng(config.seed)

        noise_std_q = np.asarray(config.noise_std_q, dtype=np.float64)
        noise_std_dq = np.asarray(config.noise_std_dq, dtype=np.float64)
        self._std = np.concat([noise_std_q, noise_std_dq])
        


    # ──────────────────────────────────────────────────────────────────────
    # Квантование
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def _apply_quantization(
        value: float, resolution: int | float, sensor_type: str
    ) -> float:
        """
        Симуляция дискретности уровней датчика.

        Parameters
        ----------
        value : float
            Непрерывное физическое значение.
        resolution : int | float
            Разрядность энкодера (для угловых датчиков) или
            шаг оптической линейки (для датчика положения тележки).
        sensor_type : {"encoder", "cart"}
            Тип датчика:
            - ``"encoder"`` — угловой энкодер (пересчёт через :math:`2\\pi / \\text{resolution}`);
            - ``"cart"`` — датчик положения каретки.

        Returns
        -------
        float
            Квантованное значение в исходных единицах (рад / м).
        """
        if sensor_type == "encoder":
            step = 2.0 * np.pi / int(resolution)
            return float(np.round(value / step) * step)
        elif sensor_type == "cart":
            step = float(resolution)
            return float(np.round(value / step) * step)
        else:
            raise ValueError(
                f"Unknown sensor_type='{sensor_type}'. "
                f"Expected 'encoder' or 'cart'."
            )

    # ──────────────────────────────────────────────────────────────────────
    # Основной метод
    # ──────────────────────────────────────────────────────────────────────

    def get_telemetry(
        self, raw_q: np.ndarray, raw_dq: np.ndarray
    ) -> np.ndarray:
        """
        Преобразовать чистые координаты ОУ в зашумлённый квантованный
        вектор телеметрии.
        """
        # raw_q и raw_dq УЖЕ numpy массивы! Не конвертируем!
        q = raw_q
        dq = raw_dq
        
        # Квантование inline (без вызова функций)
        cart_step = self._cart_step
        enc1 = self._encoder_res_1
        enc2 = self._encoder_res_2
        
        # Используем astype(int) вместо round - БЫСТРЕЕ!
        x_q = (q[0] // cart_step) * cart_step
        th1_q = (q[1] // enc1) * enc1
        th2_q = (q[2] // enc2) * enc2
        
        # Создаем массив напрямую из уже существующих значений
        # Используем view где возможно
        measured = np.empty(6, dtype=np.float64)
        measured[0] = x_q
        measured[1] = th1_q
        measured[2] = th2_q
        measured[3] = dq[0]
        measured[4] = dq[1]
        measured[5] = dq[2]
        
        # Добавляем шум (in-place для экономии памяти)
        noise = self._rng.normal(0.0, self._std)
        measured += noise
        
        # Возвращаем без создания промежуточных объектов
        return measured
