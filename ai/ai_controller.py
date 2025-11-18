"""AI controller for monsters with advanced behaviors."""
import numpy as np


class AIController:
    """Manages AI for monsters with tactical behaviors."""

    def __init__(self, level):
        """Initialize AI controller.

        Args:
            level: Game level
        """
        self.level = level
        self.monsters = []
        self.update_timer = 0.0
        self.tactical_update_interval = 0.5  # Update tactics every 0.5s

    def add_monster(self, monster):
        """Add monster to AI system."""
        self.monsters.append(monster)
        # Initialize AI data if not present
        if not hasattr(monster, 'ai_data'):
            monster.ai_data = {
                'flanking_target': None,
                'retreat_position': None,
                'last_attack_time': 0.0,
                'coordination_group': None,
                'aggression_level': 1.0  # 0.0 = cautious, 1.0 = aggressive
            }

    def remove_monster(self, monster):
        """Remove monster from AI system."""
        if monster in self.monsters:
            self.monsters.remove(monster)

    def update(self, dt, player):
        """Update all monster AI with advanced behaviors.

        Args:
            dt: Delta time
            player: Player entity
        """
        self.update_timer += dt

        # Periodic tactical updates (less frequent for performance)
        if self.update_timer >= self.tactical_update_interval:
            self._update_tactical_decisions(player)
            self.update_timer = 0.0

        # Update individual monsters
        for monster in self.monsters[:]:
            if monster.is_dead():
                self.remove_monster(monster)
                continue

            # Basic target acquisition
            if not monster.target and player:
                distance = monster.distance_to(player)
                if distance < monster.sight_range:
                    monster.set_target(player)

            # Apply advanced AI behaviors
            if monster.target:
                self._apply_advanced_behavior(monster, player, dt)

    def _update_tactical_decisions(self, player):
        """Update tactical decisions for all monsters.

        Args:
            player: Player entity
        """
        if not player:
            return

        active_monsters = [m for m in self.monsters if not m.is_dead() and m.target]

        # Group coordination: assign flanking positions
        if len(active_monsters) >= 2:
            self._coordinate_group_attack(active_monsters, player)

        # Individual tactical assessment
        for monster in active_monsters:
            self._assess_monster_tactics(monster, player)

    def _coordinate_group_attack(self, monsters, player):
        """Coordinate multiple monsters to attack from different angles.

        Args:
            monsters: List of active monsters
            player: Player entity
        """
        player_pos = player.position
        num_monsters = len(monsters)

        # Assign flanking angles around player
        for i, monster in enumerate(monsters):
            # Calculate ideal angle for this monster (spread around player)
            angle = (2 * np.pi * i) / num_monsters

            # Calculate flanking position at preferred range
            flank_distance = monster.preferred_range * 1.5
            flank_x = player_pos[0] + np.cos(angle) * flank_distance
            flank_z = player_pos[2] + np.sin(angle) * flank_distance

            monster.ai_data['flanking_target'] = np.array(
                [flank_x, player_pos[1], flank_z], dtype=np.float32
            )
            monster.ai_data['coordination_group'] = 'group_1'

    def _assess_monster_tactics(self, monster, player):
        """Assess and update individual monster tactics.

        Args:
            monster: Monster entity
            player: Player entity
        """
        # Calculate health ratio
        health_ratio = monster.health / monster.max_health

        # Adjust aggression based on health
        if health_ratio < 0.3:
            # Low health: become cautious, consider retreating
            monster.ai_data['aggression_level'] = 0.3
            
            # Find retreat position (away from player)
            direction_away = monster.position - player.position
            direction_away[1] = 0
            if np.linalg.norm(direction_away) > 0:
                direction_away = direction_away / np.linalg.norm(direction_away)
                retreat_distance = 5.0
                monster.ai_data['retreat_position'] = (
                    monster.position + direction_away * retreat_distance
                )
        elif health_ratio < 0.6:
            # Medium health: balanced approach
            monster.ai_data['aggression_level'] = 0.7
            monster.ai_data['retreat_position'] = None
        else:
            # High health: aggressive
            monster.ai_data['aggression_level'] = 1.0
            monster.ai_data['retreat_position'] = None

    def _apply_advanced_behavior(self, monster, player, dt):
        """Apply advanced AI behaviors to monster.

        Args:
            monster: Monster entity
            player: Player entity
            dt: Delta time
        """
        distance = monster.distance_to(player)
        aggression = monster.ai_data.get('aggression_level', 1.0)

        # RETREAT BEHAVIOR (low health)
        if monster.ai_data.get('retreat_position') is not None:
            self._execute_retreat(monster, player)
            return

        # FLANKING BEHAVIOR (coordinated attack)
        if monster.ai_data.get('flanking_target') is not None:
            self._execute_flanking(monster, player)
            return

        # RANGED BEHAVIOR with tactical positioning
        if monster.is_ranged:
            self._execute_ranged_tactics(monster, player, aggression)
        # MELEE BEHAVIOR
        else:
            self._execute_melee_tactics(monster, player, aggression)

    def _execute_retreat(self, monster, player):
        """Execute retreat behavior.

        Args:
            monster: Monster entity
            player: Player entity
        """
        retreat_pos = monster.ai_data['retreat_position']
        direction = retreat_pos - monster.position
        direction[1] = 0

        distance_to_retreat = np.linalg.norm(direction)

        if distance_to_retreat > 1.0:
            # Move towards retreat position
            direction = direction / distance_to_retreat
            monster.physics.velocity[0] = direction[0] * monster.move_speed * 1.2
            monster.physics.velocity[2] = direction[2] * monster.move_speed * 1.2
        else:
            # Reached retreat position, hold ground
            monster.physics.velocity[0] = 0
            monster.physics.velocity[2] = 0
            # Still face and attack player if in range
            if monster.distance_to(player) <= monster.attack_range:
                if monster.attack_cooldown <= 0:
                    monster.perform_attack()
                    monster.attack_cooldown = 1.0 / monster.attack_rate

    def _execute_flanking(self, monster, player):
        """Execute flanking maneuver.

        Args:
            monster: Monster entity
            player: Player entity
        """
        flank_target = monster.ai_data['flanking_target']
        direction = flank_target - monster.position
        direction[1] = 0

        distance_to_flank = np.linalg.norm(direction)

        if distance_to_flank > 1.5:
            # Move to flanking position
            direction = direction / distance_to_flank
            monster.physics.velocity[0] = direction[0] * monster.move_speed
            monster.physics.velocity[2] = direction[2] * monster.move_speed
        else:
            # Reached flanking position, attack from here
            player_distance = monster.distance_to(player)
            if player_distance <= monster.attack_range:
                # Stop and attack
                monster.physics.velocity[0] = 0
                monster.physics.velocity[2] = 0
                if monster.attack_cooldown <= 0:
                    monster.perform_attack()
                    monster.attack_cooldown = 1.0 / monster.attack_rate
            else:
                # Adjust position to maintain optimal range
                direction_to_player = player.position - monster.position
                direction_to_player[1] = 0
                if np.linalg.norm(direction_to_player) > 0:
                    direction_to_player = direction_to_player / np.linalg.norm(direction_to_player)
                    monster.physics.velocity[0] = direction_to_player[0] * monster.move_speed * 0.5
                    monster.physics.velocity[2] = direction_to_player[2] * monster.move_speed * 0.5

    def _execute_ranged_tactics(self, monster, player, aggression):
        """Execute tactical ranged combat.

        Args:
            monster: Monster entity
            player: Player entity
            aggression: Aggression level (0.0-1.0)
        """
        distance = monster.distance_to(player)
        direction = player.position - monster.position
        direction[1] = 0
        direction_length = np.linalg.norm(direction)

        if direction_length > 0:
            direction = direction / direction_length

        # Adjust ranges based on aggression
        min_range = monster.min_range * (2.0 - aggression)  # More cautious = stay farther
        preferred_range = monster.preferred_range * (1.5 - aggression * 0.3)

        if distance < min_range:
            # Too close! Back away
            monster.physics.velocity[0] = -direction[0] * monster.move_speed * 0.9
            monster.physics.velocity[2] = -direction[2] * monster.move_speed * 0.9
        elif distance <= monster.attack_range:
            # In attack range: strafe and attack
            import time
            strafe_dir = np.array([-direction[2], 0, direction[0]], dtype=np.float32)
            strafe_sign = 1.0 if (time.time() % 3.0) < 1.5 else -1.0

            # Strafe sideways
            strafe_speed = monster.move_speed * 0.7 * aggression
            monster.physics.velocity[0] = strafe_dir[0] * strafe_speed * strafe_sign
            monster.physics.velocity[2] = strafe_dir[2] * strafe_speed * strafe_sign

            # Attack
            if monster.attack_cooldown <= 0:
                monster.perform_attack()
                monster.attack_cooldown = 1.0 / monster.attack_rate
        else:
            # Too far, advance
            advance_speed = monster.move_speed * (0.8 + aggression * 0.4)
            monster.physics.velocity[0] = direction[0] * advance_speed
            monster.physics.velocity[2] = direction[2] * advance_speed

    def _execute_melee_tactics(self, monster, player, aggression):
        """Execute tactical melee combat.

        Args:
            monster: Monster entity
            player: Player entity
            aggression: Aggression level (0.0-1.0)
        """
        distance = monster.distance_to(player)
        direction = player.position - monster.position
        direction[1] = 0
        direction_length = np.linalg.norm(direction)

        if direction_length > 0:
            direction = direction / direction_length

        if distance <= monster.attack_range:
            # In melee range: stop and attack
            monster.physics.velocity[0] = 0
            monster.physics.velocity[2] = 0

            if monster.attack_cooldown <= 0:
                monster.perform_attack()
                monster.attack_cooldown = 1.0 / monster.attack_rate
        else:
            # Chase with aggression-modified speed
            speed_mult = 0.8 + aggression * 0.5

            # Sprint when far, slow down when close
            if distance > 5.0:
                speed_mult *= 1.3
            elif distance < 2.5:
                speed_mult *= 0.7

            monster.physics.velocity[0] = direction[0] * monster.move_speed * speed_mult
            monster.physics.velocity[2] = direction[2] * monster.move_speed * speed_mult

    def get_nearby_monsters(self, position, radius):
        """Get monsters within radius of position.

        Args:
            position: Center position
            radius: Search radius

        Returns:
            List of monsters within radius
        """
        nearby = []
        for monster in self.monsters:
            if not monster.is_dead():
                distance = np.linalg.norm(monster.position - position)
                if distance <= radius:
                    nearby.append(monster)
        return nearby
