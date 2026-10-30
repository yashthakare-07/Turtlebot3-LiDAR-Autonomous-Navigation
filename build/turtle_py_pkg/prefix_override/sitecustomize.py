import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/mob-psycho-100/ROS2_WS/install/turtle_py_pkg'
