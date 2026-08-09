#!/usr/bin/env bash
# Checks that we can actually run your submission. Not a score.
#   ./validate.sh [seed]
# Run it inside the provided image. If anything fails we cannot grade you.

# No -u: ROS's setup.bash reads unset vars, which would abort the script.
set -o pipefail

SEED="${1:--1}"
WS="$(cd "$(dirname "$0")" && pwd)/ros2_ws"
PASS=0
FAIL=0

ok()   { echo "  OK    $1"; PASS=$((PASS+1)); }
bad()  { echo "  FAIL  $1"; FAIL=$((FAIL+1)); }

echo "validating submission"
echo

# --- 1. structure --------------------------------------------------------
echo "[1/4] structure"
for f in \
  "$WS/src/auv_interfaces/package.xml" \
  "$WS/src/auv_sim/auv_sim/sim_node.py" \
  "$WS/src/auv_controller/auv_controller/controller_node.py" \
; do
  [ -f "$f" ] && ok "$(basename "$(dirname "$f")")/$(basename "$f")" \
               || bad "missing: $f"
done

# --- 2. message contract -------------------------------------------------
echo
echo "[2/4] message contract unmodified"
EXPECTED="EpisodeStatus.msg HydrophoneFix.msg VehicleState.msg VelocityCommand.msg"
ACTUAL=$(ls "$WS/src/auv_interfaces/msg" 2>/dev/null | sort | tr '\n' ' ' | sed 's/ $//')
if [ "$ACTUAL" == "$(echo $EXPECTED | tr ' ' '\n' | sort | tr '\n' ' ' | sed 's/ $//')" ]; then
  ok "all four messages present, none added or removed"
else
  bad "message set changed. expected: $EXPECTED / found: $ACTUAL"
fi

# --- 3. it builds --------------------------------------------------------
echo
echo "[3/4] colcon build"
if ( source /opt/ros/humble/setup.bash && cd "$WS" && colcon build --merge-install ) >/tmp/validate_build.log 2>&1; then
  ok "workspace builds"
else
  bad "build failed -- see /tmp/validate_build.log"
  echo
  tail -20 /tmp/validate_build.log
  echo
  echo "RESULT: NOT SUBMITTABLE ($FAIL failed)"
  exit 1
fi

# --- 4. the nodes actually run and talk ----------------------------------
echo
echo "[4/4] smoke test (30s, realtime)"
SMOKE=$(
  source /opt/ros/humble/setup.bash
  source "$WS/install/setup.bash"
  timeout 40 ros2 launch auv_sim pinger.launch.py seed:="$SEED" mode:=realtime 2>&1
)

grep -q "sim ready"      <<<"$SMOKE" && ok "simulator starts"      || bad "simulator did not start"
grep -q "controller up"  <<<"$SMOKE" && ok "controller starts"     || bad "controller did not start"
if grep -qE "Traceback|Exception" <<<"$SMOKE"; then
  bad "a node raised an exception"
  grep -A5 "Traceback" <<<"$SMOKE" | head -12
else
  ok "no exceptions"
fi

echo
if [ "$FAIL" -eq 0 ]; then
  echo "RESULT: SUBMITTABLE  ($PASS checks passed)"
  echo "This does not mean your controller is good -- only that we can run it."
  exit 0
else
  echo "RESULT: NOT SUBMITTABLE  ($FAIL failed, $PASS passed)"
  exit 1
fi
