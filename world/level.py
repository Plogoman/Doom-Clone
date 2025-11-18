"""Level data structure and rendering."""
import numpy as np
from OpenGL.GL import *
from world.bsp import BSPTree
from world.sector import Sector
from world.wall import Wall
from renderer.vertex_buffer import VertexBuffer


class Level:
    """Represents a game level with geometry and entities."""

    def __init__(self, name="Untitled"):
        """Initialize level.

        Args:
            name: Level name
        """
        self.name = name
        self.sectors = []
        self.walls = []
        self.bsp_tree = BSPTree()

        # Spawn points
        self.player_spawn = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.monster_spawns = []
        self.item_spawns = []

        # Rendering data
        self.vertex_buffers = {}  # sector_id -> vertex buffer

    def add_sector(self, sector):
        """Add sector to level.

        Args:
            sector: Sector object
        """
        self.sectors.append(sector)

    def add_wall(self, wall):
        """Add wall to level.

        Args:
            wall: Wall object
        """
        self.walls.append(wall)
        if wall.sector:
            wall.sector.add_wall(wall)

    def build(self):
        """Build BSP tree and prepare rendering data."""
        print(f"\n🏗️  Building level '{self.name}'...")
        print(f"  Sectors: {len(self.sectors)}, Walls: {len(self.walls)}")

        # Build BSP tree
        self.bsp_tree.build(self.walls, self.sectors)

        # Generate geometry for each sector
        for sector in self.sectors:
            self._generate_sector_geometry(sector)

        print(f"✓ Level build complete - {len(self.vertex_buffers)} vertex buffers created\n")

    def _generate_sector_geometry(self, sector):
        """Generate vertex buffers for sector (separate for walls, floor, ceiling).

        Args:
            sector: Sector to generate geometry for
        """
        wall_vertices = []
        floor_vertices = []
        ceiling_vertices = []

        # Generate wall geometry
        for wall in sector.walls:
            wall_verts = self._generate_wall_vertices(wall)
            wall_vertices.extend(wall_verts)

        # Generate floor/ceiling (simplified - just a quad)
        if sector.walls:
            floor_verts, ceiling_verts = self._generate_floor_ceiling(sector)
            floor_vertices.extend(floor_verts)
            ceiling_vertices.extend(ceiling_verts)

        # Create separate vertex buffers for walls, floor, and ceiling
        if wall_vertices:
            vertex_array = np.array(wall_vertices, dtype=np.float32)
            self.vertex_buffers[f'sector_{sector.id}_walls'] = VertexBuffer(vertex_array)

        if floor_vertices:
            vertex_array = np.array(floor_vertices, dtype=np.float32)
            self.vertex_buffers[f'sector_{sector.id}_floor'] = VertexBuffer(vertex_array)

        if ceiling_vertices:
            vertex_array = np.array(ceiling_vertices, dtype=np.float32)
            self.vertex_buffers[f'sector_{sector.id}_ceiling'] = VertexBuffer(vertex_array)

        total_verts = len(wall_vertices) + len(floor_vertices) + len(ceiling_vertices)
        print(f"  Sector {sector.id}: Generated {total_verts} vertices (walls:{len(wall_vertices)} floor:{len(floor_vertices)} ceiling:{len(ceiling_vertices)})")

    def _generate_wall_vertices(self, wall):
        """Generate vertices for a wall.

        Args:
            wall: Wall object

        Returns:
            List of vertices
        """
        vertices = []

        floor_h = wall.sector.floor_height
        ceil_h = wall.sector.ceiling_height

        # Wall quad (2 triangles)
        x1, y1, z1 = wall.start
        x2, y2, z2 = wall.end

        # Lower vertices (floor)
        v0 = [x1, floor_h, z1, 0.0, 0.0]
        v1 = [x2, floor_h, z2, 1.0, 0.0]

        # Upper vertices (ceiling)
        v2 = [x2, ceil_h, z2, 1.0, 1.0]
        v3 = [x1, ceil_h, z1, 0.0, 1.0]

        # Two triangles
        vertices.extend([v0, v1, v2])  # Triangle 1
        vertices.extend([v0, v2, v3])  # Triangle 2

        return vertices

    def _generate_floor_ceiling(self, sector):
        """Generate floor and ceiling for sector.

        Args:
            sector: Sector object

        Returns:
            Tuple of (floor_vertices, ceiling_vertices)
        """
        floor_vertices = []
        ceiling_vertices = []

        # Simplified: create bounding box floor/ceiling
        if not sector.walls:
            return floor_vertices, ceiling_vertices

        # Find bounding box
        min_x = min_z = float('inf')
        max_x = max_z = float('-inf')

        for wall in sector.walls:
            min_x = min(min_x, wall.start[0], wall.end[0])
            max_x = max(max_x, wall.start[0], wall.end[0])
            min_z = min(min_z, wall.start[2], wall.end[2])
            max_z = max(max_z, wall.start[2], wall.end[2])

        # Floor (counter-clockwise winding when viewed from above)
        floor_h = sector.floor_height
        floor_vertices.extend([
            [min_x, floor_h, min_z, 0.0, 0.0],
            [max_x, floor_h, max_z, 1.0, 1.0],
            [max_x, floor_h, min_z, 1.0, 0.0],

            [min_x, floor_h, min_z, 0.0, 0.0],
            [min_x, floor_h, max_z, 0.0, 1.0],
            [max_x, floor_h, max_z, 1.0, 1.0],
        ])

        # Ceiling (counter-clockwise winding when viewed from below)
        ceil_h = sector.ceiling_height
        ceiling_vertices.extend([
            [min_x, ceil_h, min_z, 0.0, 0.0],
            [max_x, ceil_h, min_z, 1.0, 0.0],
            [max_x, ceil_h, max_z, 1.0, 1.0],

            [min_x, ceil_h, min_z, 0.0, 0.0],
            [max_x, ceil_h, max_z, 1.0, 1.0],
            [min_x, ceil_h, max_z, 0.0, 1.0],
        ])

        return floor_vertices, ceiling_vertices

    def render(self, shader, texture_manager):
        """Render level geometry with separate textures for walls/floor/ceiling.

        Args:
            shader: Shader program
            texture_manager: Texture manager
        """
        # Set model matrix to identity
        model = np.identity(4, dtype=np.float32)
        shader.set_mat4('model', model)
        shader.set_int('textureSampler', 0)

        # Render all sectors
        for sector in self.sectors:
            # Update light level for this sector
            shader.set_float('lightLevel', sector.light_level)

            # Render walls with white/light gray texture
            texture_manager.bind_texture('wall', 0)
            wall_buffer_key = f'sector_{sector.id}_walls'
            if wall_buffer_key in self.vertex_buffers:
                self.vertex_buffers[wall_buffer_key].draw()

            # Render floor with dark gray texture
            texture_manager.bind_texture('floor', 0)
            floor_buffer_key = f'sector_{sector.id}_floor'
            if floor_buffer_key in self.vertex_buffers:
                self.vertex_buffers[floor_buffer_key].draw()

            # Render ceiling with medium gray texture
            texture_manager.bind_texture('ceiling', 0)
            ceiling_buffer_key = f'sector_{sector.id}_ceiling'
            if ceiling_buffer_key in self.vertex_buffers:
                self.vertex_buffers[ceiling_buffer_key].draw()

    def get_spawn_position(self):
        """Get player spawn position.

        Returns:
            Spawn position [x, y, z]
        """
        return self.player_spawn.copy()

    def cleanup(self):
        """Clean up level resources."""
        for vb in self.vertex_buffers.values():
            vb.delete()
        self.vertex_buffers.clear()
