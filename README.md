# RL — Reinforcement Learning Controllers

Короткое описание

Проект предоставляет набор симуляций и контроллеров (PID, DDPG) для обучения и тестирования методов управления и подкрепления. Предназначен для исследователей, студентов и инженеров, которым нужно быстро запустить эксперименты с контроллерами и визуализацией.

Файлы проекта

- Основной исполняемый скрипт: [`main.py`](main.py:1)
- Контроллеры: каталог [`packages/controllers/`](packages/controllers/:1)
- Симуляции и GUI: каталог [`packages/simulation/`](packages/simulation/:1)
- Короткий ролик с демонстрацией: [`output.mp4`](output.mp4:1)

Установка

1. Клонируйте репозиторий.
2. Рекомендуется использовать Python 3.10+ и виртуальное окружение:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install poetry
poetry install
```

Если вы не используете Poetry, установите зависимости напрямую из [`pyproject.toml`](pyproject.toml:1) или из `packages/*/pyproject.toml`.

Быстрый запуск

1. Запустите основную симуляцию (пример):

```bash
python main.py
```

2. Конкретный пример: запуск PID-контроллера (если `main.py` поддерживает аргументы):

```bash
python main.py --controller PID
```

Структура проекта (важные файлы)

- [`main.py`](main.py:1) — точка входа для запуска симуляций и контроллеров.
- [`packages/controllers/PID/pid.py`](packages/controllers/PID/pid.py:1) — пример реализации PID.
- [`packages/controllers/DDPG/ddpg.py`](packages/controllers/DDPG/ddpg.py:1) — пример DDPG-контроллера.
- [`packages/simulation/CO/engine.py`](packages/simulation/CO/engine.py:1) — движок симуляции.
- [`output.mp4`](output.mp4:1) — короткий ролик с демонстрацией работы симуляции/контроллера.

Как использовать видео в README

Ниже встроена короткая демонстрация работы симуляции. Воспроизведите файл прямо на странице (если платформа поддерживает) или скачайте локально.

<video controls width="640">
  <source src="output.mp4" type="video/mp4">
  Ваш браузер не поддерживает встроенное воспроизведение видео. Скачайте файл: [`output.mp4`](output.mp4:1)
</video>

Примечание: GitHub отображает mp4-файлы в браузере — если видео не воспроизводится в превью README, откройте напрямую файл [`output.mp4`](output.mp4:1).

Примеры использования кода

Пример: импорт контроллера PID в вашем скрипте

```python
from packages.controllers.PID.pid import PIDController

pid = PIDController(kp=1.0, ki=0.1, kd=0.05)
control = pid.update(setpoint=1.0, measurement=0.2)
```

Пример запуска симуляции программно

```python
from packages.simulation.CO.engine import SimulationEngine

engine = SimulationEngine()
engine.run(steps=1000)
```

Разработка и вклад

- Код организован по пакетам в каталоге [`packages/`](packages/:1). Для добавления нового контроллера создайте подпакет в [`packages/controllers/`](packages/controllers/:1) с собственным `pyproject.toml` и README.
- Запуск тестов/статического анализа: добавьте необходимые инструменты в `pyproject.toml` и запускайте через Poetry или напрямую.

Полезные команды

- Запуск основной программы: `python main.py` — [`main.py`](main.py:1)
- Установка зависимостей через poetry: `poetry install`
- Запуск конкретного подпакета: `python -m packages.simulation.GUI.gui` (пример — уточните имя модуля)

Лицензия

Укажите лицензию, например MIT, добавив файл [`LICENSE`](LICENSE:1) в корень репозитория.

Контакты

Если у вас есть вопросы или предложения — откройте issue или pull request в репозитории.

Файлы для чтения

- Этот README: [`README.md`](README.md:1)
- Демонстрация: [`output.mp4`](output.mp4:1)
