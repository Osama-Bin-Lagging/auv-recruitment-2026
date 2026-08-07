#!/usr/bin/env bash
# Run this BEFORE you submit.
#
# It checks the things that would otherwise make your submission ungradeable --
# missing files, a modified message contract, a workspace that does not build,
# a controller that never publishes. It does NOT tell you your score.
#
#   ./validate.sh <your_roll_number>
#
# Run it inside the provided Docker image. If every check says OK, we can grade
# your submission. If any check fails, we cannot, and you will score zero on a
# question you may well have solved.

set -uo pipefail

SEED="${1:-0}"
WS="$(cd "$(dirname "$0")" && pwd)/ros2_ws"
PASS=0
FAIL=0

ok()   { echo "  OK    $1"; PASS=$((PASS+1)); }
bad()  { echo "  FAIL  $1"; FAIL=$((FAIL+1)); }

echo "validating submission (seed $SEED)"
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

# --- 2. the message contract is fixed ------------------------------------
# Both your nodes and our grading simulator are built against these exact
# definitions. If you change them, your controller cannot talk to our sim.
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
