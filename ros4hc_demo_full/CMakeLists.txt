cmake_minimum_required(VERSION 3.8)
project(ros4hc_full)

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)

install(
  FILES ros4hc-demo-full.service
  DESTINATION /usr/lib/systemd/system
)

ament_package()
