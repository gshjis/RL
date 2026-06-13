"""Диалоговые окна для PendulumViewer (в отдельном модуле)."""

from __future__ import annotations

import pygame
from typing import Tuple

from .constants import BLACK, WHITE, GREEN, GRAY, FPS


def ask_recording(screen: pygame.Surface, clock: pygame.time.Clock) -> bool:
    """Показать диалог перед стартом: записывать ли видео."""
    font = pygame.font.SysFont("Consolas", 20, bold=True)
    dialog_w, dialog_h = 520, 140
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()
    dialog_rect = pygame.Rect((WIDTH - dialog_w) // 2, (HEIGHT - dialog_h) // 2, dialog_w, dialog_h)
    btn_yes = pygame.Rect(dialog_rect.right - 180, dialog_rect.bottom - 50, 70, 32)
    btn_no = pygame.Rect(dialog_rect.right - 90, dialog_rect.bottom - 50, 70, 32)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                if event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                    return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if btn_yes.collidepoint(mx, my):
                    return True
                if btn_no.collidepoint(mx, my):
                    return False

        screen.fill(BLACK)
        pygame.draw.rect(screen, (30, 30, 30), dialog_rect)
        txt = font.render("Record simulation to video?", True, GREEN)
        screen.blit(txt, (dialog_rect.x + 20, dialog_rect.y + 20))
        hint = font.render("Press Y / N or click a button", True, GRAY)
        screen.blit(hint, (dialog_rect.x + 20, dialog_rect.y + 60))

        pygame.draw.rect(screen, (50, 120, 50), btn_yes)
        pygame.draw.rect(screen, (120, 50, 50), btn_no)
        yes_s = font.render("Yes", True, WHITE)
        no_s = font.render("No", True, WHITE)
        screen.blit(yes_s, (btn_yes.x + 18, btn_yes.y + 6))
        screen.blit(no_s, (btn_no.x + 22, btn_no.y + 6))

        pygame.display.flip()
        clock.tick(FPS)


def ask_save_video(screen: pygame.Surface, clock: pygame.time.Clock, n_frames: int) -> bool:
    """Диалог сохранения видео после записи."""
    font = pygame.font.SysFont("Consolas", 18, bold=True)
    dialog_w, dialog_h = 560, 140
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()
    dialog_rect = pygame.Rect((WIDTH - dialog_w) // 2, (HEIGHT - dialog_h) // 2, dialog_w, dialog_h)
    btn_yes = pygame.Rect(dialog_rect.right - 180, dialog_rect.bottom - 50, 70, 32)
    btn_no = pygame.Rect(dialog_rect.right - 90, dialog_rect.bottom - 50, 70, 32)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                if event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                    return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if btn_yes.collidepoint(mx, my):
                    return True
                if btn_no.collidepoint(mx, my):
                    return False

        screen.fill(BLACK)
        pygame.draw.rect(screen, (30, 30, 30), dialog_rect)
        txt = font.render(f"Save recorded video from {n_frames} frames?", True, GREEN)
        screen.blit(txt, (dialog_rect.x + 20, dialog_rect.y + 20))
        hint = font.render("Press Y / N or click a button", True, GRAY)
        screen.blit(hint, (dialog_rect.x + 20, dialog_rect.y + 60))

        pygame.draw.rect(screen, (50, 120, 50), btn_yes)
        pygame.draw.rect(screen, (120, 50, 50), btn_no)
        yes_s = font.render("Yes", True, WHITE)
        no_s = font.render("No", True, WHITE)
        screen.blit(yes_s, (btn_yes.x + 18, btn_yes.y + 6))
        screen.blit(no_s, (btn_no.x + 22, btn_no.y + 6))

        pygame.display.flip()
        clock.tick(FPS)


def ask_input_target(screen: pygame.Surface, clock: pygame.time.Clock, current: float, min_x: float | None, max_x: float | None) -> float | None:
    """Показать простой инлайн-диалог ввода числового значения для target x.

    Возвращает число или None при отмене.
    """
    font = pygame.font.SysFont("Consolas", 18, bold=True)
    dialog_w, dialog_h = 420, 120
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()
    dialog_rect = pygame.Rect((WIDTH - dialog_w) // 2, (HEIGHT - dialog_h) // 2, dialog_w, dialog_h)
    input_rect = pygame.Rect(dialog_rect.x + 20, dialog_rect.y + 40, dialog_w - 40, 30)
    btn_ok = pygame.Rect(dialog_rect.right - 180, dialog_rect.bottom - 40, 70, 28)
    btn_cancel = pygame.Rect(dialog_rect.right - 90, dialog_rect.bottom - 40, 70, 28)
    text = f"{current:.3f}"
    active = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_RETURN:
                    try:
                        val = float(text)
                        if (min_x is not None and val < min_x) or (max_x is not None and val > max_x):
                            # ignore out of range
                            pass
                        else:
                            return val
                    except Exception:
                        pass
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    ch = event.unicode
                    if ch and (ch.isdigit() or ch in '.-'):
                        text += ch
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if btn_ok.collidepoint(mx, my):
                    try:
                        val = float(text)
                        if (min_x is None or min_x <= val) and (max_x is None or val <= max_x):
                            return val
                    except Exception:
                        pass
                if btn_cancel.collidepoint(mx, my):
                    return None

        screen.fill((10, 10, 10))
        pygame.draw.rect(screen, (30, 30, 30), dialog_rect)
        title = font.render("Enter target X:", True, (200, 200, 200))
        screen.blit(title, (dialog_rect.x + 20, dialog_rect.y + 10))
        pygame.draw.rect(screen, (50, 50, 50), input_rect)
        txt_surf = font.render(text, True, (220, 220, 220))
        screen.blit(txt_surf, (input_rect.x + 6, input_rect.y + 4))
        pygame.draw.rect(screen, (50, 120, 50), btn_ok)
        pygame.draw.rect(screen, (120, 50, 50), btn_cancel)
        ok_s = font.render("OK", True, (255, 255, 255))
        cancel_s = font.render("Cancel", True, (255, 255, 255))
        screen.blit(ok_s, (btn_ok.x + 18, btn_ok.y + 4))
        screen.blit(cancel_s, (btn_cancel.x + 6, btn_cancel.y + 4))

        pygame.display.flip()
        clock.tick(FPS)
