"""Обёртка для обработки событий — EventController."""

from __future__ import annotations

import pygame
from typing import Any

from .input_handling import handle_events


class EventController:
    """Класс-адаптер для обработки событий и управления состоянием цикла."""

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock) -> None:
        self.screen = screen
        self.clock = clock

    def poll(self) -> dict[str, Any]:
        """Вернуть действия, полученные из очереди событий."""
        return handle_events(self.screen, self.clock)

