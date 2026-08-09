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
# Content hashes, not filenames: adding a range field to HydrophoneFix and
# populating it from the simulator would otherwise pass this check.
echo
echo "[2/4] message contract unmodified"
MSG_DIR="$WS/src/auv_interfaces/msg"
EXPECTED_HASHES="EpisodeStatus.msg:603c26f30a431f373caf1576ed1eb6f35ae07ee49ff03b598cc5c83d2b693152
HydrophoneFix.msg:73eec3b609c8b4d8ca89f2b77bb3c37abc25b860560b427334476f7a7cebb428
VehicleState.msg:f24e645a32d82b750ec1b978c5b4b6bd781bd5993b55e728e8957e64f6337195
VelocityCommand.msg:4a7dc4adbb6d24ef60469ef11721ae1113ac5129ee8a54abcffc323ccbd9de8c"

if command -v sha256sum >/dev/null 2>&1; then
  HASH_CMD="sha256sum"
else
  HASH_CMD="shasum -a 256"
fi

CONTRACT_OK=1
while IFS=: read -r name want; do
  path="$MSG_DIR/$name"
  if [ ! -f "$path" ]; then
    bad "missing message: $name"
    CONTRACT_OK=0
    continue
  fi
  got=$($HASH_CMD "$path" | cut -d" " -f1)
  if [ "$got" != "$want" ]; then
    bad "$name has been modified"
    CONTRACT_OK=0
  fi
done <<< "$EXPECTED_HASHES"

EXTRA=$(ls "$MSG_DIR" 2>/dev/null | grep -v -e EpisodeStatus.msg -e HydrophoneFix.msg \
        -e VehicleState.msg -e VelocityCommand.msg || true)
if [ -n "$EXTRA" ]; then
  bad "extra message files: $(echo $EXTRA | tr '\n' ' ')"
  CONTRACT_OK=0
fi

[ "$CONTRACT_OK" = "1" ] && ok "all four messages present and unmodified"

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
