from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'turtle_py_pkg'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.*')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mob-psycho-100',
    maintainer_email='283800372+yashthakare-07@users.noreply.github.com',
    description='TurtleBot3 Gazebo and Nav2 assignment bringup for ROS 2 Jazzy',
    license='Apache-2.0',
    entry_points={'console_scripts': []},
)
