cmake_minimum_required(VERSION 3.5)
project(pcl_ros)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic -fPIC)
endif()

## Find system dependencies
find_package(Eigen3 REQUIRED)
find_package(PCL REQUIRED QUIET COMPONENTS common features filters io segmentation surface)

## Find ROS package dependencies
find_package(ament_cmake REQUIRED)
find_package(pcl_conversions REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_components REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_eigen REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(tf2_ros REQUIRED)

set(dependencies
  pcl_conversions
  rclcpp
  rclcpp_components
  sensor_msgs
  geometry_msgs
  tf2
  tf2_eigen
  tf2_geometry_msgs
  tf2_ros
  EIGEN3
  PCL
)

## Declare the pcl_ros_tf library
add_library(pcl_ros_tf src/transforms.cpp)
target_include_directories(pcl_ros_tf PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include/${PROJECT_NAME}>
    ${PCL_INCLUDE_DIRS}  # 添加PCL头文件路径
    ${EIGEN3_INCLUDE_DIRS}
)
ament_target_dependencies(pcl_ros_tf
  ${dependencies}
)

### 关键修改：修复 pcl_ros_filters 库配置 ###
add_library(pcl_ros_filters SHARED
  src/pcl_ros/filters/extract_indices.cpp
  src/pcl_ros/filters/filter.cpp
  src/pcl_ros/filters/passthrough.cpp
  src/pcl_ros/filters/project_inliers.cpp
  src/pcl_ros/filters/radius_outlier_removal.cpp
  src/pcl_ros/filters/statistical_outlier_removal.cpp
  src/pcl_ros/filters/voxel_grid.cpp
  src/pcl_ros/filters/crop_box.cpp
)
# 1. 添加头文件包含路径（关键缺失项）
target_include_directories(pcl_ros_filters PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include/${PROJECT_NAME}>
  ${PCL_INCLUDE_DIRS}
  ${EIGEN3_INCLUDE_DIRS}
)
# 2. 链接依赖库
target_link_libraries(pcl_ros_filters 
  pcl_ros_tf 
  ${PCL_LIBRARIES}
)
ament_target_dependencies(pcl_ros_filters ${dependencies})

# 3. 注册所有过滤器组件（保留原有配置，确保CropBox被正确注册）
rclcpp_components_register_node(pcl_ros_filters
  PLUGIN "pcl_ros::ExtractIndices"
  EXECUTABLE filter_extract_indices_node
)
rclcpp_components_register_node(pcl_ros_filters
  PLUGIN "pcl_ros::PassThrough"
  EXECUTABLE filter_passthrough_node
)
rclcpp_components_register_node(pcl_ros_filters
  PLUGIN "pcl_ros::ProjectInliers"
  EXECUTABLE filter_project_inliers_node
)
rclcpp_components_register_node(pcl_ros_filters
  PLUGIN "pcl_ros::RadiusOutlierRemoval"
  EXECUTABLE filter_radius_outlier_removal_node
)
rclcpp_components_register_node(pcl_ros_filters
  PLUGIN "pcl_ros::StatisticalOutlierRemoval"
  EXECUTABLE filter_statistical_outlier_removal_node
)
rclcpp_components_register_node(pcl_ros_filters
  PLUGIN "pcl_ros::CropBox"  # CropBox组件注册
  EXECUTABLE filter_crop_box_node
)
rclcpp_components_register_node(pcl_ros_filters
  PLUGIN "pcl_ros::VoxelGrid"
  EXECUTABLE filter_voxel_grid_node
)
# 4. 移除ROS1的class_loader_hide_library_symbols（ROS2中无效，会导致组件隐藏）
# class_loader_hide_library_symbols(pcl_ros_filters)  # 注释掉这行！

### Tools 部分保持不变 ###
add_library(pcd_to_pointcloud_lib SHARED tools/pcd_to_pointcloud.cpp)
target_link_libraries(pcd_to_pointcloud_lib
  ${PCL_LIBRARIES})
target_include_directories(pcd_to_pointcloud_lib PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include/${PROJECT_NAME}>
  ${PCL_INCLUDE_DIRS})
ament_target_dependencies(pcd_to_pointcloud_lib
  rclcpp
  rclcpp_components
  sensor_msgs
  pcl_conversions)
rclcpp_components_register_node(pcd_to_pointcloud_lib
  PLUGIN "pcl_ros::PCDPublisher"
  EXECUTABLE pcd_to_pointcloud)

add_library(pointcloud_to_pcd_lib SHARED tools/pointcloud_to_pcd.cpp)
target_link_libraries(pointcloud_to_pcd_lib
  ${PCL_LIBRARIES})
target_include_directories(pointcloud_to_pcd_lib PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include/${PROJECT_NAME}>
  ${PCL_INCLUDE_DIRS})
ament_target_dependencies(pointcloud_to_pcd_lib
  rclcpp
  rclcpp_components
  sensor_msgs
  pcl_conversions
  tf2_eigen
  tf2_ros)
rclcpp_components_register_node(pointcloud_to_pcd_lib
  PLUGIN "pcl_ros::PointCloudToPCD"
  EXECUTABLE pointcloud_to_pcd)

#############
## Testing ##
#############

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()

  find_package(ament_cmake_gtest REQUIRED)
  add_subdirectory(tests/filters)
endif()

#############
## Install ##
#############

install(
  DIRECTORY include/
  DESTINATION include/${PROJECT_NAME}
)

install(
  TARGETS
    pcl_ros_tf
    pcd_to_pointcloud_lib
    pcl_ros_filters
    pointcloud_to_pcd_lib
  EXPORT export_pcl_ros
  RUNTIME DESTINATION bin
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  INCLUDES DESTINATION include/${PROJECT_NAME}  # 新增：指定安装的头文件路径
)

install(DIRECTORY plugins samples
  DESTINATION share/${PROJECT_NAME})

# Export old-style CMake variables
ament_export_include_directories("include/${PROJECT_NAME}")
ament_export_libraries(pcl_ros_tf pcl_ros_filters)  # 新增：导出filters库

# Export modern CMake targets
ament_export_targets(export_pcl_ros HAS_LIBRARY_TARGET)

ament_export_dependencies(${dependencies})

ament_package()