"""Main game class integrating all systems."""
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
import numpy as np

class DoomCloneGame:
    """Main game class."""

    def __init__(self):
        """Initialize game."""
        self.engine = Engine()
        self.renderer = Renderer()
        self.renderer.window = self.engine.window  # Pass window reference to renderer
        self.audio_manager = AudioManager()

        # Create colored placeholder textures for monsters
        self.renderer.texture_manager.create_solid_color_texture(
            'monster_imp', (200, 50, 50, 255)  # Red/brown for Imp
        )
        self.renderer.texture_manager.create_solid_color_texture(
            'monster_demon', (220, 120, 180, 255)  # Pink for Demon (Pinky!)
        )

        # Create fireball texture (BRIGHT orange for visibility)
        self.renderer.texture_manager.create_solid_color_texture(
            'projectile_fireball', (255, 180, 0, 255)  # Very bright orange
        )

        # Create ammo box texture (gold/yellow for bullets)
        self.renderer.texture_manager.create_solid_color_texture(
            'item_ammo_bullets', (255, 220, 0, 255)  # Gold/yellow for bullet ammo
        )

        # Create wall texture (bright for contrast with floor)
        self.renderer.texture_manager.create_solid_color_texture(
            'wall', (200, 200, 200, 255)  # Light gray/white walls
        )

        # Create floor and ceiling textures
        self.renderer.texture_manager.create_solid_color_texture(
            'floor', (80, 80, 80, 255)  # Dark gray floor
        )
        self.renderer.texture_manager.create_solid_color_texture(
            'ceiling', (120, 120, 120, 255)  # Lighter gray ceiling
        )

        # Initialize HUD
        self.hud = HUD(self.engine.window.width, self.engine.window.height)

        # Load test level
        self.level = LevelLoader.create_test_level()

        # Create player
        spawn_pos = self.level.get_spawn_position()
        self.player = Player(spawn_pos)

        # Set initial camera direction to face North wall (-Z direction)
        self.player.camera.yaw = -np.pi / 2  # Face North (towards -Z)
        self.player.camera._update_vectors()

        # Give player starting weapon
        pistol = Pistol()
        self.player.equip_weapon(pistol, 1)

        # Entity list (initialize before spawning monsters!)
        self.entities = []

        # Initialize systems
        self.input_manager = InputManager(self.player)
        self.physics_system = PhysicsSystem(self.level)
        self.ai_controller = AIController(self.level)

        # Spawn test monsters
        self._spawn_test_monsters()

        # Spawn test items
        self._spawn_test_items()

        # Connect systems to engine
        self.engine.renderer = self.renderer
        self.engine.input_manager = self.input_manager
        self.engine.audio_manager = self.audio_manager
        self.engine.ai_controller = self.ai_controller
        self.engine.physics_system = self.physics_system
        self.engine.level = self.level
        self.engine.player = self.player
        self.engine.entities = self.entities
        self.engine.hud = self.hud

        # Add player to physics
        self.physics_system.add_entity(self.player)

    def _spawn_test_monsters(self):
        """Spawn test monsters in level.

        Room is 10x10 from -5 to +5 on X and Z axes.
        Player spawns at (0, 0.6, 0) facing north (-Z).
        """
        # Spawn an Imp (back right corner, away from player, above floor)
        imp = Imp(position=np.array([3.5, 0.8, 3.5], dtype=np.float32))
        imp.set_target(self.player)
        imp.entity_list = self.entities  # Give Imp access to spawn projectiles
        self.entities.append(imp)
        self.ai_controller.add_monster(imp)
        self.physics_system.add_entity(imp)

        # Spawn a Demon (back left corner, away from player, above floor)
        demon = Demon(position=np.array([-3.5, 0.7, 3.5], dtype=np.float32))
        demon.set_target(self.player)
        self.entities.append(demon)
        self.ai_controller.add_monster(demon)
        self.physics_system.add_entity(demon)

    def _spawn_test_items(self):
        """Spawn test items in level.

        Room is 10x10 from -5 to +5 on X and Z axes.
        Player spawns at (0, 0.6, 0) facing north (-Z).
        """
        from entities.item import AmmoBox

        # Spawn bullet ammo box near center (easy to see and reach, above floor)
        ammo_box = AmmoBox(
            position=np.array([2.0, 0.3, -2.0], dtype=np.float32),
            ammo_type='bullets',
            amount=20  # Gives 20 bullets
        )
        self.entities.append(ammo_box)
        print(f"  💰 Spawned bullet ammo box at position (2.0, 0.3, -2.0)")

    def run(self):
        """Start the game."""
        print("Starting Doom Clone...")
        print("Controls:")
        print("  WASD / Arrow Keys - Move")
        print("  Mouse - Look around")
        print("  Left Click - Fire weapon")
        print("  Space - Jump")
        print("  1-7 - Switch weapons")
        print("  ESC - Quit")
        print()

        # Override engine update to include our systems
        original_update = self.engine._update

        def custom_update():
            """Custom update with additional systems."""
            original_update()

            # Update physics
            self.physics_system.update(self.engine.delta_time)

            # Update AI
            self.ai_controller.update(self.engine.delta_time, self.player)

            # Handle weapon fire
            self._handle_weapon_fire()

            # Handle collisions
            self._handle_collisions()

        self.engine._update = custom_update

        # Run engine
        self.engine.run()

    def _handle_weapon_fire(self):
        """Handle weapon fire raycasting."""
        if not hasattr(self.player, '_weapon_fire_data'):
            return

        fire_data_list = self.player._weapon_fire_data[:]
        self.player._weapon_fire_data.clear()

        for fire_data in fire_data_list:
            origin = fire_data['origin']
            direction = fire_data['direction']
            damage = fire_data['damage']

            # Raycast against all entities
            closest_hit = None
            closest_dist = float('inf')

            for entity in self.entities:
                if not entity.active or not hasattr(entity, 'aabb'):
                    continue

                # Get entity AABB
                entity_aabb = entity.aabb.translate(entity.position)

                # Ray-AABB intersection
                hit, t_near, t_far = entity_aabb.intersect_ray(origin, direction)

                if hit and t_near >= 0 and t_near < closest_dist:
                    closest_dist = t_near
                    closest_hit = entity

            # Apply damage to closest hit
            if closest_hit and hasattr(closest_hit, 'take_damage'):
                hit_pos = origin + direction * closest_dist
                print(f"  ✓ Hit {closest_hit.__class__.__name__} for {damage} damage! (distance: {closest_dist:.1f})")

                # Track health before damage
                was_alive = closest_hit.health > 0

                closest_hit.take_damage(damage, self.player)

                # Check if we killed it
                if was_alive and closest_hit.health <= 0:
                    self.player.kills += 1
                    print(f"  💀 {closest_hit.__class__.__name__} killed! Total kills: {self.player.kills}")

    def _handle_collisions(self):
        """Handle entity collisions."""
        if not self.level or not self.player:
            return

        # Player-wall collisions
        player_aabb = self.player.aabb.translate(self.player.position)
        for wall in self.level.walls:
            self.player.position = CollisionSystem.resolve_aabb_wall_collision(
                self.player.position,
                self.player.aabb,
                wall
            )

        # Monster-wall collisions and projectile collisions
        from entities.projectile import Projectile
        for entity in self.entities[:]:
            if hasattr(entity, 'aabb') and entity.active:
                # Wall collisions
                entity_aabb = entity.aabb.translate(entity.position)
                for wall in self.level.walls:
                    # Projectiles destroy on wall hit
                    if isinstance(entity, Projectile):
                        collides, _, _ = CollisionSystem.check_aabb_wall_collision(entity_aabb, wall)
                        if collides:
                            entity.destroy()
                            break
                    else:
                        entity.position = CollisionSystem.resolve_aabb_wall_collision(
                            entity.position,
                            entity.aabb,
                            wall
                        )

                # Projectile-entity collisions
                if isinstance(entity, Projectile) and entity.active:
                    proj_aabb = entity.aabb.translate(entity.position)

                    # Check hit on player
                    if entity.owner != self.player:
                        player_aabb = self.player.aabb.translate(self.player.position)
                        if CollisionSystem.check_aabb_collision(proj_aabb, player_aabb):
                            entity.on_hit(self.player)
                            continue

                    # Check hit on monsters
                    for other in self.entities:
                        if other != entity and other != entity.owner and other.active:
                            if hasattr(other, 'aabb'):
                                other_aabb = other.aabb.translate(other.position)
                                if CollisionSystem.check_aabb_collision(proj_aabb, other_aabb):
                                    entity.on_hit(other)
                                    break

        # Item pickup detection
        from entities.item import Item
        for entity in self.entities[:]:
            if isinstance(entity, Item) and entity.active:
                # Check distance to player
                distance = np.linalg.norm(entity.position - self.player.position)
                if distance < entity.pickup_range:
                    # Try to pick up item
                    if entity.on_pickup(self.player):
                        print(f"  ✓ Picked up {entity.__class__.__name__}!")
