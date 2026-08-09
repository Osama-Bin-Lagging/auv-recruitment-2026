# ROS 2 Humble + Gazebo Fortress + ros_gz, with a browser-based GUI.
# Multi-arch: one tag, both amd64 and arm64. Docker picks the right one, so
# Windows/Intel and Apple Silicon candidates run the same command.
#
# The two architectures are NOT built the same way, and that is the whole
# reason this file has a branch in it:
#
#   amd64: ros-humble-ros-gz-sim is a Debian package. Install it, ~2 min.
#   arm64: no such package for arm64 jammy (only the bridge/image/interfaces
#           shims are published), so ros_gz has to be compiled from source.
#           ~15 min, and it must be built SERIALLY: ros_gz_bridge instantiates
#           enough message-conversion templates that parallel jobs exhaust the
#           memory of a typical Docker VM and the build dies with
#           "cannot allocate memory".
FROM ros:humble-ros-base

SHELL ["/bin/bash", "-c"]
ARG DEBIAN_FRONTEND=noninteractive
ARG TARGETARCH

# --- Fortress from the OSRF repo (it is not in the ROS or Ubuntu repos) ------
RUN apt-get update && apt-get install -y --no-install-recommends \
      wget gnupg ca-certificates git \
    && wget -qO /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg \
         https://packages.osrfoundation.org/gazebo.gpg \
    && echo "deb [arch=${TARGETARCH} signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] \
http://packages.osrfoundation.org/gazebo/ubuntu-stable jammy main" \
         > /etc/apt/sources.list.d/gazebo-stable.list \
    && apt-get update && apt-get install -y --no-install-recommends \
      ignition-fortress \
      ros-humble-xacro \
      python3-pip python3-colcon-common-extensions \
      python3-matplotlib \
    && rm -rf /var/lib/apt/lists/*

# --- Headless X + noVNC: the GUI is a browser tab, not an X server ----------
# Chosen over X11 forwarding because it behaves identically on macOS, Windows
# and Linux -- no XQuartz, no DISPLAY juggling, no per-OS instructions.
RUN apt-get update && apt-get install -y --no-install-recommends \
      xvfb x11vnc novnc websockify \
      libgl1-mesa-dri mesa-utils \
    && rm -rf /var/lib/apt/lists/*

# --- ros_gz: apt on amd64, source on arm64 ----------------------------------
ENV GZ_VERSION=fortress \
    IGNITION_VERSION=fortress
RUN if [ "$TARGETARCH" = "amd64" ]; then \
      apt-get update && apt-get install -y --no-install-recommends \
        ros-humble-ros-gz-sim ros-humble-ros-gz-bridge \
        ros-humble-ros-gz-image ros-humble-ros-gz-interfaces \
      && rm -rf /var/lib/apt/lists/* \
      && mkdir -p /ws/install && echo '# apt build' > /ws/install/.apt ; \
    else \
      apt-get update && apt-get install -y --no-install-recommends \
        libignition-gazebo6-dev libignition-transport11-dev \
        libignition-msgs8-dev libignition-sensors6-dev \
        libignition-rendering6-dev libignition-math6-dev \
        libignition-common4-dev libignition-plugin-dev \
        libignition-fuel-tools7-dev \
      && mkdir -p /ws/src && cd /ws/src \
      && git clone https://github.com/gazebosim/ros_gz.git -b humble --depth 1 \
      && cd /ws \
      && rosdep install -r -y -i --from-paths src --rosdistro humble \
           --skip-keys="ignition-gazebo6 ignition-msgs8 ignition-transport11 \
ignition-sensors6 ignition-rendering6 ignition-math6 ignition-common4 \
ignition-fuel-tools7" \
      && source /opt/ros/humble/setup.bash \
      && MAKEFLAGS=-j1 colcon build --merge-install \
           --executor sequential --parallel-workers 1 \
           --cmake-args -DCMAKE_BUILD_TYPE=Release \
      && rm -rf /var/lib/apt/lists/* /ws/build /ws/log /ws/src ; \
    fi

COPY start-gui.sh /start-gui.sh
RUN chmod +x /start-gui.sh \
    && echo 'source /opt/ros/humble/setup.bash' >> /root/.bashrc \
    && echo '[ -f /ws/install/setup.bash ] && source /ws/install/setup.bash' >> /root/.bashrc

ENV LIBGL_ALWAYS_SOFTWARE=1 \
    DISPLAY=:1

WORKDIR /work
EXPOSE 6080
