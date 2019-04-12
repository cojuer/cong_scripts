#!/bin/bash

# Run experiment without kernel statistics collection.
# After scenario iperf3 statistics files are available.
# Usage:
# build - builds environment to run experiments (no QoS)
# run
# 

build_testbed() {
    ip netns add src
    ip netns add dst

    ip link add src0 type veth peer name dst0

    ip link set src0 netns src
    ip link set dst0 netns dst

    ip netns exec src ifconfig src0 10.0.0.1/24 up
    ip netns exec dst ifconfig dst0 10.0.0.2/24 up
}

clear_testbed() {
    ip netns del src
    ip netns del dst
}

set_qos() {
    local nspace="${1}"
    local intf="${2}"
    local rate="${3}"
    local delay="${4}"
    local jitter="${5}"
    local loss="${6}"

    ip netns exec ${nspace} tc qdisc add dev ${intf} root handle 1: tbf rate "${rate}" burst 1536b limit 1500000
    if [ "${loss}" = "0.0" ]; then
      ip netns exec ${nspace} tc qdisc add dev ${intf} parent 1:1 handle 10: netem delay "${delay}" "${jitter}"
    else
      ip netns exec ${nspace} tc qdisc add dev ${intf} parent 1:1 handle 10: netem delay "${delay}" "${jitter}" loss random "${loss}"
    fi
}

# bw, delay, jitter, loss, alg
run_experiment() {
    local rate="${1}mbit"
    local delay="${2}ms"
    local jitter="${3}ms"
    local loss="${4}"
    local algo="${5}"
    local attempt="${6}"
    local exp_time="${7}"

    set_qos src src0 ${rate} ${delay} ${jitter} ${loss}
    set_qos dst dst0 ${rate} ${delay} ${jitter} ${loss}

    ip netns exec dst iperf3 -s -J > "Data/net_${algo}_${1}_${2}_${3}_${loss}_${attempt}_server.json" & SRV_PID=$!
    sleep 1
    ip netns exec src iperf3 -c 10.0.0.2 -C ${algo} -t ${exp_time} -J > "Data/net_${algo}_${1}_${2}_${3}_${loss}_${attempt}_client.json"
    sleep 1
    kill -s SIGTERM ${SRV_PID}
}


usage() {
  >&2 echo "Configure testbed to test TCP CC algorithms"
  >&2 echo "Option list:"
  >&2 echo " -b  -- build testbed"
  >&2 echo " -c  -- clear testbed"
  >&2 echo " -r  -- run experiments"
  exit 1
}

case $1 in
  -b) build_testbed ;;
  -c) clear_testbed ;;
  -r) run_experiment ${2} ${3} ${4} ${5} ${6} ${7} ${8} ;;
  *) usage ;;
esac
