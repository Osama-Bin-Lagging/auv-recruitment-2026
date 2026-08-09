#!/bin/bash
# Serve the Gazebo GUI to a browser tab.
#
# Xvfb gives us a display with no monitor, x11vnc exports it over VNC, and
# websockify wraps that in WebSockets so noVNC can render it in a browser.
# Chosen over X11 forwarding because it behaves identically on macOS, Windows
# and Linux -- no XQuartz, no X server setup, no DISPLAY juggling.
set -e

export DISPLAY=:1
export LIBGL_ALWAYS_SOFTWARE=1

Xvfb :1 -screen 0 1600x900x24 >/tmp/xvfb.log 2>&1 &
sleep 2
x11vnc -display :1 -forever -shared -nopw -quiet -rfbport 5900 >/tmp/x11vnc.log 2>&1 &
sleep 1
websockify --web=/usr/share/novnc 6080 localhost:5900 >/tmp/websockify.log 2>&1 &
sleep 2

echo "=================================================="
echo "  Gazebo GUI:  http://localhost:6080/vnc.html"
echo "  (no password; click Connect)"
echo "=================================================="

source /opt/ros/humble/setup.bash
# Only the arm64 build has a /ws overlay; amd64 installs ros_gz from apt.
# An unguarded source here kills the script under `set -e`.
if [ -f /ws/install/setup.bash ]; then
  source /ws/install/setup.bash
fi

if [ -n "$1" ]; then
  echo "launching world: $1"
  ign gazebo -r "$1"
else
  exec bash
fi
