# A single acoustic bearing fix from the body-mounted hydrophone.
#
# Published on /auv/hydrophone at the ping rate (NOT at the control rate).
# `valid` is false when no fix is available this ping -- a dropped ping, or the
# pinger in its silent window. These two cases are indistinguishable on purpose:
# real hardware cannot tell them apart either.
#
# bearing is RELATIVE to vehicle heading, in radians, wrapped to [-pi, pi].
# There is no range field. There will never be a range field.
std_msgs/Header header
bool valid
float32 bearing
