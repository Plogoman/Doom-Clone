#!/usr/bin/env python3
"""Doom Clone - Main entry point.

Run with: uv run main.py
"""
from game import DoomCloneGame
import traceback

def main():
    """Main function."""
    try:
        game = DoomCloneGame()
        game.run()
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main()