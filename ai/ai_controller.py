"""AI controller for monsters."""


class AIController:
    """Manages AI for monsters."""

    def __init__(self, level):
        """Initialize AI controller.

        Args:
            level: Game level
        """
        self.level = level
        self.monsters = []

    def add_monster(self, monster):
        """Add monster to AI system."""
        self.monsters.append(monster)

    def remove_monster(self, monster):
        """Remove monster from AI system."""
        if monster in self.monsters:
            self.monsters.remove(monster)

    def update(self, dt, player):
        """Update all monster AI.

        Args:
            dt: Delta time
            player: Player entity
        """
        for monster in self.monsters[:]:
            if monster.is_dead():
                self.remove_monster(monster)
                continue

            # Set player as target if in range
            if not monster.target and player:
                distance = monster.distance_to(player)
                if distance < monster.sight_range:
                    monster.set_target(player)
