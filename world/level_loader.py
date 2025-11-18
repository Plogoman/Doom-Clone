"""Level loading from files."""
import json
from world.level import Level
from world.sector import Sector
from world.wall import Wall
import numpy as np


class LevelLoader:
    """Loads levels from JSON files."""

    @staticmethod
    def load_from_json(filepath):
        """Load level from JSON file.

        Args:
            filepath: Path to JSON level file

        Returns:
            Level object
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        level = Level(data.get('name', 'Untitled'))

        # Load sectors
        sectors_by_id = {}
        for sector_data in data.get('sectors', []):
            sector = Sector(
                sector_data['id'],
                sector_data.get('floor_height', 0.0),
                sector_data.get('ceiling_height', 2.5)
            )
            sector.floor_texture = sector_data.get('floor_texture', 'default_floor')
            sector.ceiling_texture = sector_data.get('ceiling_texture', 'default_ceiling')
            sector.light_level = sector_data.get('light_level', 1.0)

            sectors_by_id[sector.id] = sector
            level.add_sector(sector)

        # Load walls
        for wall_data in data.get('walls', []):
            start = np.array(wall_data['start'], dtype=np.float32)
            end = np.array(wall_data['end'], dtype=np.float32)

            sector = sectors_by_id.get(wall_data['sector_id'])
            other_sector = sectors_by_id.get(wall_data.get('other_sector_id'))

            wall = Wall(start, end, sector, other_sector)
            wall.middle_texture = wall_data.get('texture', 'default_wall')

            level.add_wall(wall)

        # Load spawn points
        if 'player_spawn' in data:
            level.player_spawn = np.array(data['player_spawn'], dtype=np.float32)

        level.monster_spawns = [
            np.array(spawn, dtype=np.float32)
            for spawn in data.get('monster_spawns', [])
        ]

        level.item_spawns = [
            {
                'position': np.array(spawn['position'], dtype=np.float32),
                'type': spawn['type']
            }
            for spawn in data.get('item_spawns', [])
        ]

        # Build BSP and geometry
        level.build()

        return level

    @staticmethod
    def create_test_level():
        """Create a simple test level.

        Returns:
            Level object
        """
        level = Level("Test Level")

        # Create a simple room
        sector = Sector(0, floor_height=0.0, ceiling_height=2.5)
        level.add_sector(sector)

        # Create walls for a square room (10x10)
        walls_data = [
            ([-5, 0, -5], [5, 0, -5]),  # North wall
            ([5, 0, -5], [5, 0, 5]),    # East wall
            ([5, 0, 5], [-5, 0, 5]),    # South wall
            ([-5, 0, 5], [-5, 0, -5]),  # West wall
        ]

        for start, end in walls_data:
            wall = Wall(start, end, sector)
            level.add_wall(wall)

        # Set spawn in center of room
        level.player_spawn = np.array([0.0, 0.6, 0.0], dtype=np.float32)

        # Build level
        level.build()

        return level
