"""Main game engine and game loop."""
import pygame
from pygame.locals import *
from core.window import Window
from core.config import FPS_TARGET, SHOW_FPS


class Engine:
    """Main game engine managing game loop and systems."""

    def __init__(self):
        """Initialize game engine."""
        self.window = Window()
        self.running = False
        self.delta_time = 0.0

        # FPS display
        self.fps_update_timer = 0.0
        self.fps_update_interval = 0.5  # Update FPS twice per second

        # Systems (to be initialized by game)
        self.renderer = None
        self.input_manager = None
        self.audio_manager = None
        self.ai_controller = None
        self.physics_system = None
        self.level = None
        self.player = None
        self.entities = []
        self.hud = None

    def run(self):
        """Start the main game loop."""
        self.running = True

        while self.running:
            # Calculate delta time
            self.delta_time = self.window.tick(FPS_TARGET)

            # Process events
            self._process_events()

            # Update game state
            self._update()

            # Render
            self._render()

            # Display FPS (update only twice per second to avoid spam)
            if SHOW_FPS:
                self.fps_update_timer += self.delta_time
                if self.fps_update_timer >= self.fps_update_interval:
                    self.fps_update_timer = 0.0
                    fps = self.window.get_fps()
                    from core.config import WINDOW_TITLE
                    pygame.display.set_caption(f"{WINDOW_TITLE} - FPS: {fps:.1f}")

        self._cleanup()

    def _process_events(self):
        """Process pygame events."""
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
        """Update game state."""
        if self.input_manager:
            self.input_manager.update(self.delta_time)

        # Update AI controller (manages monster AI)
        if self.ai_controller:
            self.ai_controller.update(self.delta_time, self.player)

        if self.player:
            self.player.update(self.delta_time)

        # Update all entities
        for entity in self.entities[:]:  # Copy list to allow removal during iteration
            entity.update(self.delta_time)
            if hasattr(entity, 'is_dead') and entity.is_dead():
                self.entities.remove(entity)

        # Update physics system (handles collisions)
        if self.physics_system:
            self.physics_system.update(self.delta_time)

    def _render(self):
        """Render the scene."""
        self.window.clear()

        # Render 3D world and entities
        if self.renderer and self.level:
            self.renderer.render(self.level, self.player, self.entities)

        # Render HUD as OpenGL overlay
        if self.hud and self.player:
            hud_surface = self.hud.render(self.player)
            if hud_surface and self.renderer:
                self.renderer.render_hud_overlay(hud_surface)

        self.window.swap_buffers()

    def _cleanup(self):
        """Clean up resources."""
        if self.audio_manager:
            self.audio_manager.cleanup()

        self.window.close()

    def stop(self):
        """Stop the game loop."""
        self.running = False
