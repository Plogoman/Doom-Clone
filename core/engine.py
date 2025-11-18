"""Main game engine and game loop - clear screen before Game Over UI."""
import pygame
from pygame.locals import *
from core.window import Window
from core.config import FPS_TARGET, SHOW_FPS

class Engine:
    """Main game engine managing game loop and systems with proper Game Over screen clearing."""

    def __init__(self):
        self.window = Window()
        self.running = False
        self.delta_time = 0.0
        self.fps_update_timer = 0.0
        self.fps_update_interval = 0.5
        # Systems
        self.renderer = None
        self.input_manager = None
        self.audio_manager = None
        self.ai_controller = None
        self.physics_system = None
        self.level = None
        self.player = None
        self.entities = []
        self.hud = None
        self.game_over_screen = None  # Expect set by game

    def run(self):
        self.running = True
        while self.running:
            self.delta_time = self.window.tick(FPS_TARGET)
            self._process_events()
            self._update()
            self._render()
            if SHOW_FPS:
                self.fps_update_timer += self.delta_time
                if self.fps_update_timer >= self.fps_update_interval:
                    self.fps_update_timer = 0.0
                    fps = self.window.get_fps()
                    from core.config import WINDOW_TITLE
                    pygame.display.set_caption(f"{WINDOW_TITLE} - FPS: {fps:.1f}")
        self._cleanup()

    def _process_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                elif self.input_manager:
                    self.input_manager.on_key_down(event.key)
            elif event.type == KEYUP:
                if self.input_manager:
                    self.input_manager.on_key_up(event.key)
            elif event.type == MOUSEMOTION:
                if self.input_manager:
                    self.input_manager.on_mouse_motion(event.rel)
            elif event.type == MOUSEBUTTONDOWN:
                if self.input_manager:
                    self.input_manager.on_mouse_button_down(event.button)
            elif event.type == MOUSEBUTTONUP:
                if self.input_manager:
                    self.input_manager.on_mouse_button_up(event.button)

    def _update(self):
        if self.input_manager:
            self.input_manager.update(self.delta_time)
        # Halt game logic if player is dead
        if self.player and self.player.health <= 0:
            return
        if self.ai_controller:
            self.ai_controller.update(self.delta_time, self.player)
        if self.player:
            self.player.update(self.delta_time)
        for entity in self.entities[:]:
            entity.update(self.delta_time)
            if hasattr(entity, 'is_dead') and entity.is_dead():
                self.entities.remove(entity)
        if self.physics_system:
            self.physics_system.update(self.delta_time)

    def _render(self):
        self.window.clear()
        # Show only GAME OVER overlay if dead
        if self.player and self.player.health <= 0 and self.game_over_screen:
            surface = pygame.display.get_surface()
            # Fill screen solid black
            surface.fill((0, 0, 0))
            # Now render game over message
            self.game_over_screen.render(surface, kills=getattr(self.player, 'kills', 0), restart_hint=True)
            self.window.swap_buffers()
            return
        # Else regular render
        if self.renderer and self.level:
            self.renderer.render(self.level, self.player, self.entities)
        if self.hud and self.player:
            hud_surface = self.hud.render(self.player)
            if hud_surface and self.renderer:
                self.renderer.render_hud_overlay(hud_surface)
        self.window.swap_buffers()

    def _cleanup(self):
        if self.audio_manager:
            self.audio_manager.cleanup()
        self.window.close()
    def stop(self):
        self.running = False
