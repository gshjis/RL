import numpy as np
from packages.simulation.CO.datatypes import SensorConfig



class SensorBlock:
    def __init__(self, config: SensorConfig) -> None:
        self._cart_step = config.cart_sensor_resolution
        self._angle_step_1 = 2.0 * np.pi / config.encoder_resolution_1
        self._angle_step_2 = 2.0 * np.pi / config.encoder_resolution_2
        
        self._rng = np.random.default_rng(config.seed)
        
        noise_std_q = np.asarray(config.noise_std_q, dtype=np.float64)
        noise_std_dq = np.asarray(config.noise_std_dq, dtype=np.float64)
        self._std = np.concat([noise_std_q, noise_std_dq])
        
        self._pool_size = 2_000_000  # 2 млн шагов
        self._noise_pool = self._rng.normal(
            0.0, self._std, 
            size=(self._pool_size, 6)
        )
        self._noise_index = 0
        
        # Буфер для результата
        self._meas = np.empty(6, dtype=np.float64)

    def get_telemetry(self, raw_q: np.ndarray, raw_dq: np.ndarray) -> np.ndarray:
        q = raw_q
        dq = raw_dq
        
        # Квантование
        cs = self._cart_step
        a1 = self._angle_step_1
        a2 = self._angle_step_2
        
        meas = self._meas
        meas[0] = np.rint(q[0] / cs) * cs
        meas[1] = np.rint(q[1] / a1) * a1
        meas[2] = np.rint(q[2] / a2) * a2
        meas[3] = dq[0]
        meas[4] = dq[1]
        meas[5] = dq[2]
        
        # Берем шум из пула (без генерации!)
        noise = self._noise_pool[self._noise_index]
        self._noise_index += 1
        if self._noise_index >= self._pool_size:
            self._noise_index = 0
        
        meas += noise
        return meas
