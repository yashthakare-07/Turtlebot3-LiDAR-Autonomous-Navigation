# TurtleBot3 LiDAR Autonomous Navigation

**ROS 2 Jazzy · Gazebo Harmonic · Navigation2**

## Project summary

This project demonstrates goal-directed autonomous navigation with a TurtleBot3 Burger in a locally generated Gazebo obstacle course. The robot uses its simulated 2D LiDAR to detect obstacles and update Nav2 costmaps while Nav2 plans and executes a path to a goal selected in RViz.

The course, Gazebo world, and occupancy map are maintained together in this workspace. The map raster is generated from the same box dimensions used to build the SDF world, keeping simulated obstacles and the navigation map aligned. The project uses released ROS packages for the robot model, Gazebo integration, and Nav2; it does not introduce a custom navigation algorithm or require a custom ROS package beyond this workspace package.

## Capabilities

- One XML launch entry point starts Gazebo, the Burger model, ROS–Gazebo bridges, robot state publishing, Nav2 localization and navigation, and RViz.
- A 12 m × 12 m indoor course contains 15 rectangular barriers and four boundary walls.
- AMCL starts from the robot's configured spawn pose at `(-4.8, -4.8)` in the map frame.
- Nav2 uses the static map and AMCL for global localization, NavFn for global planning, DWB for local control, and LiDAR observations for obstacle costmaps.
- The RViz goal tool sends a destination; the robot plans and navigates autonomously to that goal while responding to detected obstacles.

## Software requirements

The workspace targets Ubuntu 24.04 with ROS 2 Jazzy and Gazebo Harmonic. Install the required ROS binary packages if they are not present:

```bash
sudo apt update
sudo apt install ros-jazzy-turtlebot3 ros-jazzy-turtlebot3-gazebo \
  ros-jazzy-navigation2 ros-jazzy-nav2-bringup ros-jazzy-ros-gz-sim \
  ros-jazzy-ros-gz-bridge ros-jazzy-rviz2
```

## Build and launch

From a terminal, run:

```bash
cd ~/ROS2_WS
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select turtle_py_pkg
source install/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtle_py_pkg autonomous_navigation.launch.xml
```

The XML launcher includes the workspace bringup and starts the full demo. Gazebo opens with the robot at its configured start pose; RViz opens with the map, LiDAR display, costmaps, and Navigation2 panel. Wait for **Navigation** and **Localization** to show **active** before sending a goal.

### Send a navigation goal

In RViz, choose **Nav2 Goal** (also labeled **2D Goal Pose** in some toolbars), click a free location on the map, and drag to indicate the desired final heading. Nav2 plans and drives the robot to that destination. Choose a destination with room around it; the map and costmaps show obstacle clearances.

Press **Ctrl+C** in the terminal running the launch to stop the stack. Do not start a second copy of the launch while the first one is running.

## Navigation architecture

| Component | Role in this project |
|---|---|
| Gazebo Harmonic | Simulates the obstacle course, Burger, physics, and sensors |
| ROS–Gazebo bridge | Publishes the simulated clock, LiDAR scan, odometry, and related robot data into ROS 2 |
| `/scan` (`sensor_msgs/msg/LaserScan`) | LiDAR observations used by Nav2 obstacle layers and local avoidance |
| `/odom` (`nav_msgs/msg/Odometry`) and TF | Robot motion estimate and transforms used by localization and control |
| AMCL | Estimates the robot pose on the supplied map, initialized at the launch spawn pose |
| Nav2 costmaps | Combine the static map with live LiDAR obstacle observations |
| NavFn planner | Computes a global route through free map space |
| DWB controller | Follows the route and selects local velocity commands while considering obstacles |
| RViz | Displays the map, robot, scan, costmaps, and goal controls |

The simulated Burger also publishes an IMU topic, but the provided Nav2 configuration does not fuse IMU data. The navigation configuration is in `src/turtle_py_pkg/config/burger_nav2.yaml`.

## Environment and map

The generated environment files are:

- `src/turtle_py_pkg/worlds/complex_obstacle_world.sdf` — Gazebo world with the floor, lighting, collision geometry, and 19 static box models (15 course barriers and four perimeter walls).
- `src/turtle_py_pkg/maps/complex_obstacle_world.yaml` — Nav2 map metadata, with origin `[-6, -6, 0]` and 0.05 m resolution.
- `src/turtle_py_pkg/maps/complex_obstacle_world.pgm` — 240 × 240 occupancy raster aligned to the world geometry.
- `src/turtle_py_pkg/scripts/generate_environment.py` — single source for box dimensions; regenerates the world and matching map.

The previous `turtlebot3_world` map YAML and raster have been removed. The current launch points to the complex course and its matching map.

### Customize the obstacle course

Edit the `OBSTACLES` list in `src/turtle_py_pkg/scripts/generate_environment.py`. Each entry defines a model name, center `(x, y)`, footprint dimensions, and height in metres. Keep the spawn point clear and preserve connected corridors wide enough for the robot. Regenerate the SDF and occupancy map, then rebuild:

```bash
python3 src/turtle_py_pkg/scripts/generate_environment.py
colcon build --symlink-install --packages-select turtle_py_pkg
```

If the spawn pose is changed, update both the `x_pose` and `y_pose` arguments in `src/turtle_py_pkg/launch/turtlebot3_nav_demo.launch.py` and the AMCL `initial_pose` in `src/turtle_py_pkg/config/burger_nav2.yaml` to the same coordinates.

## Workspace layout

```text
ROS2_WS/
├── README.md
└── src/turtle_py_pkg/
    ├── config/       # Nav2 parameters and RViz configuration
    ├── launch/       # XML entry point and underlying ROS launch description
    ├── maps/         # Generated occupancy map and metadata
    ├── scripts/      # Reproducible world/map generator
    └── worlds/       # Generated Gazebo SDF world
```

## Verification and operating scope

The package builds with `colcon`; the XML launch file resolves through the ROS 2 launch system; and the generated SDF, map metadata, and raster dimensions are checked for consistency. A live Gazebo/RViz navigation run should be demonstrated on the submission machine and captured in the required 1–2 minute recording.

This deliverable demonstrates autonomous navigation in simulation. It is not a safety-certified configuration for deployment on a physical robot. Physical operation requires validating sensor calibration, localization, footprint, controller limits, and emergency-stop behavior on the target hardware.

## References

- [ROS 2 XML launch format](https://design.ros2.org/articles/roslaunch_xml.html)
- [Nav2 documentation](https://docs.nav2.org/)
- [TurtleBot3 documentation](https://emanual.robotis.com/docs/en/platform/turtlebot3/)
