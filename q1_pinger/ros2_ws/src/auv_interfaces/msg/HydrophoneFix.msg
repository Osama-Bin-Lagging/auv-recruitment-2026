# Acoustic bearing fix. Published at the control rate, but `valid` is true
# only on a ping. False means no fix right now: a dropped ping and a silent
# pinger are indistinguishable, as on real hardware.
# bearing is relative to vehicle heading, radians, wrapped to [-pi, pi].
# There is no range field.
std_msgs/Header header
bool valid
float32 bearing
