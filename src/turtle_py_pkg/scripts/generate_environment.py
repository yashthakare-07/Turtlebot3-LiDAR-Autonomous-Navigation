#!/usr/bin/env python3
"""Generate the Gazebo obstacle course and its matching Nav2 occupancy map."""

from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
WORLD_HALF = 6.0
RESOLUTION = 0.05
WALL_HEIGHT = 1.2

# name, center x, center y, size x, size y, height. All dimensions are metres.
OBSTACLES = [
    ('west_wall', -5.9, 0.0, 0.2, 12.0, WALL_HEIGHT),
    ('east_wall', 5.9, 0.0, 0.2, 12.0, WALL_HEIGHT),
    ('south_wall', 0.0, -5.9, 11.8, 0.2, WALL_HEIGHT),
    ('north_wall', 0.0, 5.9, 11.8, 0.2, WALL_HEIGHT),
    ('barrier_01', -3.6, -3.5, 2.5, 0.55, 0.9),
    ('barrier_02', -1.0, -4.2, 0.55, 2.2, 1.2),
    ('barrier_03', 1.0, -3.3, 2.7, 0.55, 0.9),
    ('barrier_04', 4.0, -3.9, 0.55, 2.4, 1.2),
    ('barrier_05', 3.4, -1.6, 2.3, 0.55, 0.9),
    ('barrier_06', 1.0, -1.2, 0.55, 2.2, 1.2),
    ('barrier_07', -1.2, -1.3, 2.6, 0.55, 0.9),
    ('barrier_08', -4.0, -0.8, 0.55, 2.1, 1.2),
    ('barrier_09', -3.0, 1.5, 2.5, 0.55, 0.9),
    ('barrier_10', -0.4, 1.0, 0.55, 2.2, 1.2),
    ('barrier_11', 2.5, 1.3, 2.8, 0.55, 0.9),
    ('barrier_12', 4.0, 3.4, 0.55, 2.0, 1.2),
    ('barrier_13', 1.0, 4.0, 2.6, 0.55, 0.9),
    ('barrier_14', -2.0, 3.8, 0.55, 2.1, 1.2),
    ('barrier_15', -4.2, 4.2, 1.4, 0.55, 0.9),
]


def _model(name, x, y, length, width, height, index):
    z = height / 2.0
    shade = '0.24 0.52 0.76 1' if index % 2 else '0.85 0.39 0.16 1'
    return f'''    <model name="{name}">
      <static>true</static>
      <pose>{x} {y} {z} 0 0 0</pose>
      <link name="body">
        <collision name="collision">
          <geometry><box><size>{length} {width} {height}</size></box></geometry>
        </collision>
        <visual name="visual">
          <geometry><box><size>{length} {width} {height}</size></box></geometry>
          <material><ambient>{shade}</ambient><diffuse>{shade}</diffuse></material>
        </visual>
      </link>
    </model>'''


def generate_world():
    models = '\n'.join(
        _model(*obstacle, index) for index, obstacle in enumerate(OBSTACLES)
    )
    world = f'''<?xml version="1.0"?>
<sdf version="1.8">
  <world name="complex_obstacle_world">
    <physics type="ode">
      <real_time_update_rate>1000</real_time_update_rate>
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1</real_time_factor>
    </physics>
    <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"/>
    <plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"/>
    <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster"/>
    <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors">
      <render_engine>ogre2</render_engine>
    </plugin>
    <plugin filename="gz-sim-imu-system" name="gz::sim::systems::Imu"/>
    <light name="sun" type="directional">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <direction>-0.5 0.1 -0.9</direction>
    </light>
    <model name="ground_plane">
      <static>true</static>
      <link name="ground">
        <collision name="collision">
          <geometry><plane><normal>0 0 1</normal><size>12 12</size></plane></geometry>
        </collision>
        <visual name="visual">
          <geometry><plane><normal>0 0 1</normal><size>12 12</size></plane></geometry>
          <material><ambient>0.72 0.72 0.72 1</ambient><diffuse>0.72 0.72 0.72 1</diffuse></material>
        </visual>
      </link>
    </model>
{models}
  </world>
</sdf>
'''
    (PACKAGE / 'worlds' / 'complex_obstacle_world.sdf').write_text(world)


def generate_map():
    cells = round(2 * WORLD_HALF / RESOLUTION)
    pixels = bytearray([254]) * (cells * cells)

    # Occupancy-map row 0 is the north edge; world y increases upwards.
    for _name, x, y, length, width, _height in OBSTACLES:
        min_x = max(0, int(((x - length / 2) + WORLD_HALF) / RESOLUTION))
        max_x = min(cells, int(((x + length / 2) + WORLD_HALF) / RESOLUTION + 0.9999))
        min_from_south = max(0, int(((y - width / 2) + WORLD_HALF) / RESOLUTION))
        max_from_south = min(cells, int(((y + width / 2) + WORLD_HALF) / RESOLUTION + 0.9999))
        row_start = cells - max_from_south
        row_end = cells - min_from_south
        for row in range(row_start, row_end):
            start = row * cells + min_x
            pixels[start:start + (max_x - min_x)] = bytes(max_x - min_x)

    maps = PACKAGE / 'maps'
    maps.mkdir(parents=True, exist_ok=True)
    pgm = b'P5\n# Generated from generate_environment.py\n' + \
        f'{cells} {cells}\n255\n'.encode('ascii') + pixels
    (maps / 'complex_obstacle_world.pgm').write_bytes(pgm)
    (maps / 'complex_obstacle_world.yaml').write_text(
        'image: complex_obstacle_world.pgm\n'
        f'resolution: {RESOLUTION:.3f}\n'
        f'origin: [-{WORLD_HALF:.3f}, -{WORLD_HALF:.3f}, 0.000]\n'
        'negate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.196\nmode: trinary\n'
    )


if __name__ == '__main__':
    (PACKAGE / 'worlds').mkdir(parents=True, exist_ok=True)
    generate_world()
    generate_map()
    print('Generated complex_obstacle_world.sdf and matching map files.')
