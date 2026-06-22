# C++ / PyBind11 backend

Папка содержит C++ ядро симуляции CO (`co_physics.cpp`/`.hpp`)
и pybind11-биндинг (`co_bindings.cpp`).

## Требования

- **cmake** ≥ 3.20
- **C++17** компилятор (gcc ≥ 9, clang ≥ 10)
- **pybind11** — устанавливается через poetry корневого проекта:
  ```bash
  poetry add pybind11
  ```

Сборка использует Python из корневого poetry-окружения,
**не требует** создания отдельного `.venv` внутри `packages/simulation/CO/`.

## Сборка

Из **корня проекта** (`/home/gshjis/Python_projects/RL`):

```bash
# 1. Подготовить build-директорию
cd packages/simulation/CO/cpp
rm -rf build
mkdir build && cd build

# 2. Запустить cmake с Python из poetry
cmake .. \
  -DPython_EXECUTABLE="$(poetry run python -c 'import sys; print(sys.executable)')" \
  -DCMAKE_BUILD_TYPE=Release

# 3. Собрать
cmake --build . -j "$(nproc)"
```

После успешной сборки бинарный модуль появится здесь:

```
packages/simulation/CO/co_cpp.so
```

## Проверка

```bash
poetry run python -c "
from packages.simulation.CO import co_cpp as m
print('C++ backend OK:', m)
print('Functions:', [f for f in dir(m) if not f.startswith('_')])
"
```

Ожидаемый вывод:
```
C++ backend OK: <module 'co_cpp' from '.../packages/simulation/CO/co_cpp.so'>
Functions: ['NoiseForce', 'PlantParams', 'State3', 'StateDot3',
           'rk4_step', 'update_physics_cpp']
```

## Быстрая пересборка (если build уже настроен)

```bash
cd packages/simulation/CO/cpp/build
cmake --build . -j "$(nproc)"
```

Без очистки `build`-директории — cmake кеш сохраняет `Python_EXECUTABLE`.
