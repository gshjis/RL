# C++ / PyBind11 backend

Папка содержит C++ ядро симуляции CO и pybind11-биндинг.

## Сборка

1. Перейдите в build-директорию:

```bash
cd packages/simulation/CO/cpp
rm -rf build
mkdir -p build
cd build
```

2. Соберите модуль. Важно указать Python интерпретатор из `poetry`:

```bash
cmake .. \
  -DPython_EXECUTABLE="$(poetry run python -c 'import sys; print(sys.executable)')"

cmake --build . -j 2
```

3. После сборки бинарь появится рядом с пакетом Python (в `packages/simulation/CO/`).

Ожидаемый файл: `packages/simulation/CO/co_cpp.so`.

## Проверка

```bash
poetry run python -c "import packages.simulation.CO.co_cpp as m; print(m)"
```
