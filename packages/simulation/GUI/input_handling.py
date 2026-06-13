"""Обработка ввода и событий для PendulumViewer."""

from __future__ import annotations

import pygame
from typing import Any, Dict, Optional, Tuple

from .constants import WIDTH, HEIGHT, FPS


def handle_events(screen: pygame.Surface, clock: pygame.time.Clock) -> Dict[str, Any]:
    """Обработать очередь событий pygame и вернуть словарь действий.

    Возвращаемые ключи:
    - running: bool (False если нужно выйти)
    - toggle_record: bool (True если клик по кнопке записи)
    - mouse_pos: Tuple[int,int] | None
    """
    actions: Dict[str, Any] = {
        "running": True,
        "toggle_record": False,
        "mouse_pos": None,
        "quit": False,
    }

    events = list(pygame.event.get())
    for event in events:
        if event.type == pygame.QUIT:
            actions["running"] = False
            actions["quit"] = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            actions["mouse_pos"] = (mx, my)
            # Проверка кнопки записи — правая верхняя область
            btn_rect = (WIDTH - 120, 10, 110, 28)
            if btn_rect[0] <= mx <= btn_rect[0] + btn_rect[2] and btn_rect[1] <= my <= btn_rect[1] + btn_rect[3]:
                actions["toggle_record"] = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                actions["running"] = False

    # also return raw events so higher-level controllers can handle modality-specific input
    actions["events"] = events
    return actions
