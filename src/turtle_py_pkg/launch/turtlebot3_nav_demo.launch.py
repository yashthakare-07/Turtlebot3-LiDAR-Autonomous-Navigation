"""Launch TurtleBot3 in the stock obstacle world with Nav2 and RViz."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable,
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    model = os.environ.get('TURTLEBOT3_MODEL', 'burger')
    os.environ['TURTLEBOT3_MODEL'] = model

    tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    nav2_bringup = get_package_share_directory('nav2_bringup')
    local_package = get_package_share_directory('turtle_py_pkg')

    gazebo_launch = os.path.join(
        get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
    state_publisher_launch = os.path.join(
        tb3_gazebo, 'launch', 'robot_state_publisher.launch.py')
    spawn_robot_launch = os.path.join(tb3_gazebo, 'launch', 'spawn_turtlebot3.launch.py')
    world_file = os.path.join(local_package, 'worlds', 'complex_obstacle_world.sdf')
    nav_launch = os.path.join(nav2_bringup, 'launch', 'bringup_launch.py')
    map_file = os.path.join(local_package, 'maps', 'complex_obstacle_world.yaml')
    params_file = os.path.join(local_package, 'config', f'{model}_nav2.yaml')
    rviz_config = os.path.join(local_package, 'config', 'tb3_navigation2.rviz')

    start_simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch),
        launch_arguments={
            'gz_args': ['-r -v2 ', world_file],
            # Keep Nav2 and the bridge alive if the Gazebo GUI is closed.
            'on_exit_shutdown': 'false',
        }.items(),
    )
    publish_robot_state = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(state_publisher_launch),
        launch_arguments={'use_sim_time': 'true'}.items(),
    )
    spawn_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(spawn_robot_launch),
        launch_arguments={'x_pose': '-4.8', 'y_pose': '-4.8'}.items(),
    )

    start_navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(nav_launch),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'params_file': LaunchConfiguration('params_file'),
            'use_sim_time': 'true',
        }.items(),
    )
    start_rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=map_file,
                              description='Map YAML matching the complex obstacle world'),
        DeclareLaunchArgument('params_file', default_value=params_file,
                              description='Nav2 parameters for the selected TurtleBot3 model'),
        AppendEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            os.path.join(tb3_gazebo, 'models'),
        ),
        start_simulation,
        publish_robot_state,
        spawn_robot,
        # Let Gazebo start and spawn the robot before Nav2 initializes its costmaps.
        TimerAction(period=10.0, actions=[start_navigation, start_rviz]),
    ])
