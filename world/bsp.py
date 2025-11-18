"""Binary Space Partitioning tree for efficient rendering."""
import numpy as np


class BSPNode:
    """Node in BSP tree."""

    def __init__(self, partition_line=None):
        """Initialize BSP node.

        Args:
            partition_line: Line used for partitioning (start, end)
        """
        self.partition_line = partition_line
        self.front = None  # Front child node
        self.back = None  # Back child node
        self.walls = []  # Walls at this node (leaf)
        self.sector = None  # Sector for this node (leaf)
        self.is_leaf = False

    def is_point_in_front(self, point):
        """Check if point is in front of partition line.

        Args:
            point: Point to test [x, y, z]

        Returns:
            True if in front, False if behind
        """
        if not self.partition_line:
            return True

        start, end = self.partition_line
        # Cross product in 2D (XZ plane)
        dx = end[0] - start[0]
        dz = end[2] - start[2]
        px = point[0] - start[0]
        pz = point[2] - start[2]

        cross = dx * pz - dz * px
        return cross >= 0

    def __repr__(self):
        """String representation."""
        if self.is_leaf:
            return f"BSPLeaf(sector={self.sector.id if self.sector else None}, walls={len(self.walls)})"
        return f"BSPNode(has_front={self.front is not None}, has_back={self.back is not None})"


class BSPTree:
    """Binary Space Partitioning tree for level geometry."""

    def __init__(self):
        """Initialize empty BSP tree."""
        self.root = None

    def build(self, walls, sectors):
        """Build BSP tree from walls and sectors.

        Args:
            walls: List of Wall objects
            sectors: List of Sector objects
        """
        if not walls:
            return

        self.root = self._build_recursive(walls, sectors)

    def _build_recursive(self, walls, sectors):
        """Recursively build BSP tree.

        Args:
            walls: List of walls to partition
            sectors: List of sectors

        Returns:
            BSPNode
        """
        if not walls:
            return None

        # For simplicity, just create leaf nodes
        # A full BSP implementation would partition recursively
        node = BSPNode()
        node.is_leaf = True
        node.walls = walls

        # Assign sector (use first wall's sector)
        if walls:
            node.sector = walls[0].sector

        return node

    def traverse_front_to_back(self, camera_pos, callback):
        """Traverse tree from front to back relative to camera.

        Args:
            camera_pos: Camera position [x, y, z]
            callback: Function called for each node
        """
        if self.root:
            self._traverse_recursive(self.root, camera_pos, callback)

    def _traverse_recursive(self, node, camera_pos, callback):
        """Recursive traversal.

        Args:
            node: Current node
            camera_pos: Camera position
            callback: Callback function
        """
        if node.is_leaf:
            callback(node)
            return

        # Determine which side camera is on
        in_front = node.is_point_in_front(camera_pos)

        if in_front:
            # Render back first, then front
            if node.back:
                self._traverse_recursive(node.back, camera_pos, callback)
            callback(node)
            if node.front:
                self._traverse_recursive(node.front, camera_pos, callback)
        else:
            # Render front first, then back
            if node.front:
                self._traverse_recursive(node.front, camera_pos, callback)
            callback(node)
            if node.back:
                self._traverse_recursive(node.back, camera_pos, callback)

    def find_sector_at(self, x, z):
        """Find sector containing point.

        Args:
            x: X coordinate
            z: Z coordinate

        Returns:
            Sector object or None
        """
        if not self.root:
            return None

        node = self.root
        while not node.is_leaf:
            if node.is_point_in_front([x, 0, z]):
                node = node.front if node.front else node.back
            else:
                node = node.back if node.back else node.front

            if not node:
                return None

        return node.sector

    def __repr__(self):
        """String representation."""
        return f"BSPTree(root={self.root})"
