from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition

def generate_launch_description():
    # 1. 声明可配置的启动参数（方便外部传参，也可使用默认值）
    declare_min_x_arg = DeclareLaunchArgument(
        'min_x',
        default_value='0.0',
        description='CropBox filter minimum X coordinate'
    )
    declare_max_x_arg = DeclareLaunchArgument(
        'max_x',
        default_value='8.8',
        description='CropBox filter maximum X coordinate'
    )
    declare_min_y_arg = DeclareLaunchArgument(
        'min_y',
        default_value='-11.88',
        description='CropBox filter minimum Y coordinate'
    )
    declare_max_y_arg = DeclareLaunchArgument(
        'max_y',
        default_value='11.88',
        description='CropBox filter maximum Y coordinate'
    )
    declare_min_z_arg = DeclareLaunchArgument(
        'min_z',
        default_value='-2.0',
        description='CropBox filter minimum Z coordinate'
    )
    declare_max_z_arg = DeclareLaunchArgument(
        'max_z',
        default_value='3.0',
        description='CropBox filter maximum Z coordinate'
    )
    declare_keep_organized_arg = DeclareLaunchArgument(
        'keep_organized',
        default_value='false',
        description='Whether to keep the point cloud organized'
    )
    declare_negative_arg = DeclareLaunchArgument(
        'negative',
        default_value='true',
        description='Whether to apply negative filter (keep points outside the box)'
    )
    declare_input_topic_arg = DeclareLaunchArgument(
        'input_topic',
        default_value='/livox/lidar_repub',
        description='Input point cloud topic name'
    )
    declare_output_topic_arg = DeclareLaunchArgument(
        'output_topic',
        default_value='/livox/lidar3',
        description='Output cropped point cloud topic name'
    )

    # 2. 配置CropBox节点
    crop_box_node = Node(
        package='pcl_ros',
        executable='filter_crop_box_node',  # 对应CMake中生成的可执行文件
        name='crop_box_filter',  # 自定义节点名称（可覆盖默认的filter_crop_box_node）
        output='screen',  # 终端输出日志
        parameters=[{
            'min_x': LaunchConfiguration('min_x'),
            'max_x': LaunchConfiguration('max_x'),
            'min_y': LaunchConfiguration('min_y'),
            'max_y': LaunchConfiguration('max_y'),
            'min_z': LaunchConfiguration('min_z'),
            'max_z': LaunchConfiguration('max_z'),
            'keep_organized': LaunchConfiguration('keep_organized'),
            'negative': LaunchConfiguration('negative')
        }],
        # 话题重映射（将节点默认的input/output映射到指定话题）
        remappings=[
            ('input', LaunchConfiguration('input_topic')),
            ('output', LaunchConfiguration('output_topic'))
        ],
        # 可选：设置日志级别
        arguments=['--ros-args', '--log-level', 'info']
    )

    # 3. 组装LaunchDescription
    return LaunchDescription([
        # 先声明所有参数
        declare_min_x_arg,
        declare_max_x_arg,
        declare_min_y_arg,
        declare_max_y_arg,
        declare_min_z_arg,
        declare_max_z_arg,
        declare_keep_organized_arg,
        declare_negative_arg,
        declare_input_topic_arg,
        declare_output_topic_arg,
        # 再启动节点
        crop_box_node
    ])