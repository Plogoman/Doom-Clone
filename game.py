"""Main game class integrating all systems, now supporting full restart after Game Over."""
from core import Engine
from renderer import Renderer
from entities import Player
from entities.weapons import Pistol
from entities.monsters import Imp, Demon
from world import LevelLoader
from input import InputManager
from audio import AudioManager
from physics import PhysicsSystem, CollisionSystem
from ai import AIController
from ui import HUD
from ui.game_over import GameOverScreen
import numpy as np
import pygame

class DoomCloneGame:
    def __init__(self):
        self._build_game_state()

    def _build_game_state(self):
        self.engine = Engine()
        self.renderer = Renderer()
        self.renderer.window = self.engine.window
        self.audio_manager = AudioManager()
        self.renderer.texture_manager.create_solid_color_texture('monster_imp', (200, 50, 50, 255))
        self.renderer.texture_manager.create_solid_color_texture('monster_demon', (220, 120, 180, 255))
        self.renderer.texture_manager.create_solid_color_texture('projectile_fireball', (255, 180, 0, 255))
        self.renderer.texture_manager.create_solid_color_texture('item_ammo_bullets', (255, 220, 0, 255))
        self.renderer.texture_manager.create_solid_color_texture('wall', (200, 200, 200, 255))
        self.renderer.texture_manager.create_solid_color_texture('floor', (80, 80, 80, 255))
        self.renderer.texture_manager.create_solid_color_texture('ceiling', (120, 120, 120, 255))
        self.hud = HUD(self.engine.window.width, self.engine.window.height)
        self.game_over_screen = GameOverScreen(self.engine.window.width, self.engine.window.height)
        self.level = LevelLoader.create_test_level()
        spawn_pos = self.level.get_spawn_position()
        self.player = Player(spawn_pos)
        self.player.camera.yaw = -np.pi / 2
        self.player.camera._update_vectors()
        pistol = Pistol()
        self.player.equip_weapon(pistol, 1)
        self.entities = []
        self.input_manager = InputManager(self.player)
        self.physics_system = PhysicsSystem(self.level)
        self.ai_controller = AIController(self.level)
        self._spawn_test_monsters()
        self._spawn_test_items()
        self.engine.renderer = self.renderer
        self.engine.input_manager = self.input_manager
        self.engine.audio_manager = self.audio_manager
        self.engine.ai_controller = self.ai_controller
        self.engine.physics_system = self.physics_system
        self.engine.level = self.level
        self.engine.player = self.player
        self.engine.entities = self.entities
        self.engine.hud = self.hud
        self.engine.game_over_screen = self.game_over_screen
        self.physics_system.add_entity(self.player)
        self.is_game_over = False
    def _spawn_test_monsters(self):
        imp = Imp(position=np.array([3.5, 0.8, 3.5], dtype=np.float32))
        imp.set_target(self.player)
        imp.entity_list = self.entities
        self.entities.append(imp)
        self.ai_controller.add_monster(imp)
        self.physics_system.add_entity(imp)
        demon = Demon(position=np.array([-3.5, 0.7, 3.5], dtype=np.float32))
        demon.set_target(self.player)
        self.entities.append(demon)
        self.ai_controller.add_monster(demon)
        self.physics_system.add_entity(demon)
    def _spawn_test_items(self):
        from entities.item import AmmoBox
        ammo_box = AmmoBox(position=np.array([2.0, 0.3, -2.0], dtype=np.float32), ammo_type='bullets', amount=20)
        self.entities.append(ammo_box)
        print(f"  💰 Spawned bullet ammo box at position (2.0, 0.3, -2.0)")
    def run(self):
        print("Starting Doom Clone...")
        print("Controls:")
        print("  WASD / Arrow Keys - Move")
        print("  Mouse - Look around")
        print("  Left Click - Fire weapon")
        print("  Space - Jump")
        print("  1-7 - Switch weapons")
        print("  R - Restart after death")
        print("  ESC - Quit")
        print()

        # Hook into engine update to perform game-specific logic (weapon hits, collisions)
        original_update = self.engine._update
        def custom_update():
            # Run engine's normal update (handles input, player, AI, physics while alive)
            original_update()
            # Only run extra logic if player is alive
            if not self.player or self.player.health <= 0:
                return
            # Process weapon hit scans and collisions
            self._handle_weapon_fire()
            self._handle_collisions()
        self.engine._update = custom_update

        # Main loop with restart handling: run engine until exit or restart requested
        while True:
            self.engine.run()
            # If a restart was requested (via pressing R when dead), rebuild state and continue
            if getattr(self.engine, '_restart_requested', False):
                print("Restart requested! Rebuilding game state...")
                self._build_game_state()
                # Reinstall custom_update on new engine instance
                original_update = self.engine._update
                def custom_update():
                    original_update()
                    if not self.player or self.player.health <= 0:
                        return
                    self._handle_weapon_fire()
                    self._handle_collisions()
                self.engine._update = custom_update
                continue
            # Otherwise, quit the game loop
            break
    def _handle_weapon_fire(self):
        if not hasattr(self.player, '_weapon_fire_data'):
            return
        fire_data_list = self.player._weapon_fire_data[:]
        self.player._weapon_fire_data.clear()
        for fire_data in fire_data_list:
            origin = fire_data['origin']
            direction = fire_data['direction']
            damage = fire_data['damage']
            closest_hit = None
            closest_dist = float('inf')
            for entity in self.entities:
                if not entity.active or not hasattr(entity, 'aabb'):
                    continue
                entity_aabb = entity.aabb.translate(entity.position)
                hit, t_near, t_far = entity_aabb.intersect_ray(origin, direction)
                if hit and t_near >= 0 and t_near < closest_dist:
                    closest_dist = t_near
                    closest_hit = entity
            if closest_hit and hasattr(closest_hit, 'take_damage'):
                hit_pos = origin + direction * closest_dist
                print(f"  ✓ Hit {closest_hit.__class__.__name__} for {damage} damage! (distance: {closest_dist:.1f})")
                was_alive = closest_hit.health > 0
                closest_hit.take_damage(damage, self.player)
                if was_alive and closest_hit.health <= 0:
                    self.player.kills += 1
                    print(f"  💀 {closest_hit.__class__.__name__} killed! Total kills: {self.player.kills}")
    def _handle_collisions(self):
        if not self.level or not self.player:
            return
        player_aabb = self.player.aabb.translate(self.player.position)
        for wall in self.level.walls:
            self.player.position = CollisionSystem.resolve_aabb_wall_collision(
                self.player.position, self.player.aabb, wall)
        from entities.projectile import Projectile
        for entity in self.entities[:]:
            if hasattr(entity, 'aabb') and entity.active:
                entity_aabb = entity.aabb.translate(entity.position)
                for wall in self.level.walls:
                    if isinstance(entity, Projectile):
                        collides, _, _ = CollisionSystem.check_aabb_wall_collision(entity_aabb, wall)
                        if collides:
                            entity.destroy()
                            break
                    else:
                        entity.position = CollisionSystem.resolve_aabb_wall_collision(
                            entity.position, entity.aabb, wall)
                if isinstance(entity, Projectile) and entity.active:
                    proj_aabb = entity.aabb.translate(entity.position)
                    if entity.owner != self.player:
                        player_aabb = self.player.aabb.translate(self.player.position)
                        if CollisionSystem.check_aabb_collision(proj_aabb, player_aabb):
                            entity.on_hit(self.player)
                            continue
                    for other in self.entities:
                        if other != entity and other != entity.owner and other.active:
                            if hasattr(other, 'aabb'):
                                other_aabb = other.aabb.translate(other.position)
                                if CollisionSystem.check_aabb_collision(proj_aabb, other_aabb):
                                    entity.on_hit(other)
                                    break
        from entities.item import Item
        for entity in self.entities[:]:
            if isinstance(entity, Item) and entity.active:
                distance = np.linalg.norm(entity.position - self.player.position)
                if distance < entity.pickup_range:
                    if entity.on_pickup(self.player):
                        print(f"  ✓ Picked up {entity.__class__.__name__}!")
