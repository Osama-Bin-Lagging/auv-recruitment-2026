# Control output, subscribed on /auv/cmd.
#
# Velocity is commanded in the WORLD frame, in m/s, and reached through a
# first-order lag (thrusters are not instant). The magnitude of (vx, vy) is
# clamped to MAX_SPEED by the simulator -- asking for more is not an error,
# it is simply saturated.
#
# heading is a desired absolute heading in radians. It only points the
# hydrophone; it does not steer the vehicle. The vehicle is holonomic.
std_msgs/Header header
float32 vx
float32 vy
float32 heading
