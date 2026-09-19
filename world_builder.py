"""Run this to open the Karel World Builder on its own, with no robot or
running world needed:

    python world_builder.py
"""
from karel.worldbuilder import WorldBuilder

if __name__ == "__main__":
    WorldBuilder().run()
