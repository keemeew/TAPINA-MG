#!/usr/bin/env python3
import argparse
import json
import shutil
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import random
import numpy as np
from functions_ import deferred_acceptance, find_worst_switch, find_best_switch

ALL_SWITCHES = [f"s{i}" for i in range(1, 11)]
ALL_SWITCHES_UPPER = [sw.upper() for sw in ALL_SWITCHES]
MAX_STATIC_JOB_ACTIONS = 5  # tapina.p4 currently has read_worker_job1..5 and Job1..Job5

HOST_TO_TOR = {
    "h1": "s1", "h2": "s1", "h3": "s1",
    "h4": "s2", "h5": "s2", "h6": "s2",
    "h7": "s3", "h8": "s3", "h9": "s3",
    "h10": "s4", "h11": "s4", "h12": "s4",
}

HOST_MAC = {
    "h1":  "00:00:0a:00:01:01",
    "h2":  "00:00:0a:00:01:02",
    "h3":  "00:00:0a:00:01:03",
    "h4":  "00:00:0a:00:02:04",
    "h5":  "00:00:0a:00:02:05",
    "h6":  "00:00:0a:00:02:06",
    "h7":  "00:00:0a:00:03:07",
    "h8":  "00:00:0a:00:03:08",
    "h9":  "00:00:0a:00:03:09",
    "h10": "00:00:0a:00:04:0a",
    "h11": "00:00:0a:00:04:0b",
    "h12": "00:00:0a:00:04:0c",
}

HOST_IP = {
    "h1":  "10.0.1.1",
    "h2":  "10.0.1.2",
    "h3":  "10.0.1.3",
    "h4":  "10.0.2.4",
    "h5":  "10.0.2.5",
    "h6":  "10.0.2.6",
    "h7":  "10.0.3.7",
    "h8":  "10.0.3.8",
    "h9":  "10.0.3.9",
    "h10": "10.0.4.10",
    "h11": "10.0.4.11",
    "h12": "10.0.4.12",
}

SWITCH_PORTS: Dict[str, Dict[str, Tuple[int, str]]] = {
    "s1":  {"h1": (1, HOST_MAC["h1"]),  "h2": (2, HOST_MAC["h2"]),  "h3": (3, HOST_MAC["h3"]),  "s5": (4, "00:00:00:00:01:05"), "s6": (5, "00:00:00:00:01:06")},
    "s2":  {"h4": (1, HOST_MAC["h4"]),  "h5": (2, HOST_MAC["h5"]),  "h6": (3, HOST_MAC["h6"]),  "s5": (4, "00:00:00:00:02:05"), "s6": (5, "00:00:00:00:02:06")},
    "s3":  {"h7": (1, HOST_MAC["h7"]),  "h8": (2, HOST_MAC["h8"]),  "h9": (3, HOST_MAC["h9"]),  "s7": (4, "00:00:00:00:03:07"), "s8": (5, "00:00:00:00:03:08")},
    "s4":  {"h10": (1, HOST_MAC["h10"]), "h11": (2, HOST_MAC["h11"]), "h12": (3, HOST_MAC["h12"]), "s7": (4, "00:00:00:00:04:07"), "s8": (5, "00:00:00:00:04:08")},
    "s5":  {"s1": (1, "00:00:00:00:05:01"), "s2": (2, "00:00:00:00:05:02"), "s9": (3, "00:00:00:00:05:09"), "s10": (4, "00:00:00:00:05:0a")},
    "s6":  {"s1": (1, "00:00:00:00:06:01"), "s2": (2, "00:00:00:00:06:02"), "s9": (3, "00:00:00:00:06:09"), "s10": (4, "00:00:00:00:06:0a")},
    "s7":  {"s3": (1, "00:00:00:00:07:03"), "s4": (2, "00:00:00:00:07:04"), "s9": (3, "00:00:00:00:07:09"), "s10": (4, "00:00:00:00:07:0a")},
    "s8":  {"s3": (1, "00:00:00:00:08:03"), "s4": (2, "00:00:00:00:08:04"), "s9": (3, "00:00:00:00:08:09"), "s10": (4, "00:00:00:00:08:0a")},
    "s9":  {"s5": (1, "00:00:00:00:09:05"), "s6": (2, "00:00:00:00:09:06"), "s7": (3, "00:00:00:00:09:07"), "s8": (4, "00:00:00:00:09:08")},
    "s10": {"s5": (1, "00:00:00:00:0a:05"), "s6": (2, "00:00:00:00:0a:06"), "s7": (3, "00:00:00:00:0a:07"), "s8": (4, "00:00:00:00:0a:08")},
}


@dataclass
class Job:
    job_id: int
    workers: List[str]
    model_size: int = 1


def sw_num(sw: str) -> int:
    return int(sw[1:])


def host_num(host: str) -> int:
    return int(host[1:])


def mac_to_hex(mac: str) -> str:
    return "0x" + mac.replace(":", "")


def ip_to_hex(ip: str) -> str:
    return "0x" + "".join(f"{int(octet):02x}" for octet in ip.split("."))


def host_downlink_src_mac(host: str) -> str:
    parts = [int(o) for o in HOST_IP[host].split(".")]
    return f"00:01:{parts[0]:02x}:{parts[1]:02x}:{parts[2]:02x}:{parts[3]:02x}"


def build_matching_graph(ps_attach_switch: str = "s8") -> Dict[str, Dict[str, int]]:
    ps_attach_switch = ps_attach_switch.lower()
    if ps_attach_switch not in SWITCH_PORTS:
        raise ValueError(f"Unknown PS attach switch: {ps_attach_switch}")

    graph = {
        "H1": {"S1": 1}, "H2": {"S1": 1}, "H3": {"S1": 1},
        "H4": {"S2": 1}, "H5": {"S2": 1}, "H6": {"S2": 1},
        "H7": {"S3": 1}, "H8": {"S3": 1}, "H9": {"S3": 1},
        "H10": {"S4": 1}, "H11": {"S4": 1}, "H12": {"S4": 1},
        "S1": {"H1": 1, "H2": 1, "H3": 1, "S5": 1, "S6": 1},
        "S2": {"H4": 1, "H5": 1, "H6": 1, "S5": 1, "S6": 1},
        "S3": {"H7": 1, "H8": 1, "H9": 1, "S7": 1, "S8": 1},
        "S4": {"H10": 1, "H11": 1, "H12": 1, "S7": 1, "S8": 1},
        "S5": {"S1": 1, "S2": 1, "S9": 1, "S10": 1},
        "S6": {"S1": 1, "S2": 1, "S9": 1, "S10": 1},
        "S7": {"S3": 1, "S4": 1, "S9": 1, "S10": 1},
        "S8": {"S3": 1, "S4": 1, "S9": 1, "S10": 1},
        "S9": {"S5": 1, "S6": 1, "S7": 1, "S8": 1},
        "S10": {"S5": 1, "S6": 1, "S7": 1, "S8": 1},
        "PS": {ps_attach_switch.upper(): 1},
    }
    graph[ps_attach_switch.upper()]["PS"] = 1
    return graph


def jobs_from_json(path: Path):
    data = json.loads(path.read_text())
    jobs: List[Job] = []
    placement = data.get("placement", {})
    agg_switch = data.get("agg_switch", {})

    for key, value in data["jobs"].items():
        jobs.append(Job(int(key), [w.lower() for w in value["workers"]], int(value.get("model_size", 1))))
    jobs.sort(key=lambda j: j.job_id)

    normalized_agg = {int(k): str(v).lower() for k, v in agg_switch.items()}
    return jobs, placement, normalized_agg


def derive_manual_solution(
    jobs: List[Job],
    agg_map: Dict[int, str],
    k: int,
    capacity: int,
) -> Tuple[Dict[int, str], Set[str], Set[str], Dict[str, List[int]]]:
    job_ids = {job.job_id for job in jobs}

    missing = sorted(job_ids - set(agg_map.keys()))
    extra = sorted(set(agg_map.keys()) - job_ids)
    if missing:
        raise RuntimeError(f"agg_switch가 지정되지 않은 job이 있습니다: {missing}")
    if extra:
        raise RuntimeError(f"존재하지 않는 job id가 agg_switch에 들어 있습니다: {extra}")

    invalid_switches = sorted({sw for sw in agg_map.values() if sw not in ALL_SWITCHES})
    if invalid_switches:
        raise RuntimeError(f"유효하지 않은 스위치가 agg_switch에 있습니다: {invalid_switches}")

    sw_to_jobs: Dict[str, List[int]] = defaultdict(list)
    for job_id, sw in agg_map.items():
        sw_to_jobs[sw].append(job_id)

    tapina_switches = set(sw_to_jobs.keys())
    normal_switches = set(ALL_SWITCHES) - tapina_switches

    if len(tapina_switches) > k:
        raise RuntimeError(f"agg_switch 기준 TAPINA switch 수({len(tapina_switches)})가 k({k})보다 큽니다.")

    over_capacity = {sw: len(js) for sw, js in sw_to_jobs.items() if len(js) > capacity}
    if over_capacity:
        raise RuntimeError(f"capacity를 초과한 TAPINA switch가 있습니다: {over_capacity}")

    for sw in sw_to_jobs:
        sw_to_jobs[sw].sort()

    return dict(agg_map), tapina_switches, normal_switches, dict(sw_to_jobs)


def build_example_jobs() -> List[Job]:
    return [
        Job(1, ["h2", "h4", "h5", "h8", "h10", "h11"]),
        Job(2, ["h2", "h6", "h7", "h11"]),
        Job(3, ["h2", "h3", "h9"]),
        Job(4, ["h1", "h2", "h4", "h5", "h9", "h11"]),
        Job(5, ["h2", "h7", "h9", "h12"]),
    ]


def apps_from_jobs(jobs: List[Job]) -> List[List[object]]:
    return [[[w.upper() for w in job.workers], int(job.model_size)] for job in jobs]


def derive_matching_solution(
    jobs: List[Job],
    k: int,
    capacity: int,
    ps_attach_switch: str = "s8",
    candidate_switches: Optional[List[str]] = None,
) -> Tuple[Dict[int, str], Set[str], Set[str], Dict[str, List[int]]]:
    graph = build_matching_graph(ps_attach_switch)
    if candidate_switches is None:
        candidate_switches = ALL_SWITCHES_UPPER

    apps = apps_from_jobs(jobs)
    app_id_to_job = {id(apps[idx]): jobs[idx].job_id for idx in range(len(jobs))}

    switch_list, rejected_list = deferred_acceptance(graph, apps, candidate_switches, capacity)
    selected_switches = [group for group in switch_list if len(group) > 1]

    while len(selected_switches) > k:
        remove_switch = find_worst_switch(graph, selected_switches)
        selected_switches.remove(remove_switch)
        for app in remove_switch[1:]:
            rejected_list.append(app)

    selected_switch_names = [group[0] for group in selected_switches]
    final_switch_list, rejected_list_final = deferred_acceptance(graph, apps, selected_switch_names, capacity)

    agg_map: Dict[int, str] = {}
    sw_to_jobs: Dict[str, List[int]] = defaultdict(list)
    for group in final_switch_list:
        if len(group) <= 1:
            continue
        sw = group[0].lower()
        for app in group[1:]:
            job_id = app_id_to_job[id(app)]
            agg_map[job_id] = sw
            sw_to_jobs[sw].append(job_id)

    all_rejected = list(rejected_list) + list(rejected_list_final)
    if all_rejected:
        selected_switch_names_upper = [sw.upper() for sw in sorted(sw_to_jobs.keys(), key=sw_num)]
        if not selected_switch_names_upper:
            raise RuntimeError("선택된 TAPINA switch가 없습니다.")
        for app in all_rejected:
            best_sw = find_best_switch(graph, app, selected_switch_names_upper).lower()
            job_id = app_id_to_job[id(app)]
            agg_map[job_id] = best_sw
            sw_to_jobs[best_sw].append(job_id)

    missing = [job.job_id for job in jobs if job.job_id not in agg_map]
    if missing:
        raise RuntimeError(f"agg switch가 정해지지 않은 job이 있습니다: {missing}")

    tapina_switches = set(sw_to_jobs.keys())
    normal_switches = set(ALL_SWITCHES) - tapina_switches
    return agg_map, tapina_switches, normal_switches, dict(sw_to_jobs)


def bfs_path_with_source_parity(source_tor: str, agg_sw: str, src_host: str) -> List[str]:
    parity_even = (host_num(src_host) % 2 == 0)
    q = deque([[source_tor]])
    seen = {source_tor}

    while q:
        path = q.popleft()
        cur = path[-1]
        if cur == agg_sw:
            return path

        for nxt in sorted([n for n in SWITCH_PORTS[cur] if n.startswith("s")], key=sw_num):
            if nxt in seen:
                continue
            if nxt not in {source_tor, agg_sw} and ((sw_num(nxt) % 2 == 0) != parity_even):
                continue
            seen.add(nxt)
            q.append(path + [nxt])

    raise RuntimeError(f"경로를 찾지 못했습니다: src_host={src_host}, source_tor={source_tor}, agg_sw={agg_sw}")


def full_worker_path(src_host: str, agg_sw: str) -> List[str]:
    return [src_host] + bfs_path_with_source_parity(HOST_TO_TOR[src_host], agg_sw, src_host)


def bitmap_order(workers: List[str]) -> Dict[str, int]:
    return {worker: idx for idx, worker in enumerate(workers)}


def set_egress_line(port: int, dst_mac: str, src_mac: str, comment: Optional[str] = None) -> str:
    line = f"set_egress_port({port}, {mac_to_hex(dst_mac)}, {mac_to_hex(src_mac)})"
    return f"{line};{' // ' + comment if comment else ''}"


def set_adder_line(src_mac: str, dst_mac: str, comment: Optional[str] = None) -> str:
    line = f"set_adder({mac_to_hex(src_mac)}, {mac_to_hex(dst_mac)})"
    return f"{line};{' // ' + comment if comment else ''}"


def set_dst_addr_line(src_mac: str, dst_mac: str, host: str, comment: Optional[str] = None) -> str:
    line = f"set_dst_addr({mac_to_hex(src_mac)}, {mac_to_hex(dst_mac)}, {ip_to_hex(HOST_IP[host])})"
    return f"{line};{' // ' + comment if comment else ''}"


def format_dst_addr_key(job_id: int, worker_id: int) -> str:
    worker_field = f"{worker_id}"
    pre_one = "  " if worker_id < 10 else " "
    return f"({job_id}, {worker_field}," + pre_one + "1,  _)"


def next_and_prev_switch_nodes(path_nodes: List[str], sw: str) -> Tuple[Optional[str], Optional[str]]:
    idx = path_nodes.index(sw)
    prev_node = path_nodes[idx - 1] if idx - 1 >= 0 else None
    next_node = path_nodes[idx + 1] if idx + 1 < len(path_nodes) else None
    return prev_node, next_node


def switch_link_macs(sw: str, other_sw: str) -> Tuple[str, str]:
    local_mac = SWITCH_PORTS[sw][other_sw][1]
    remote_mac = SWITCH_PORTS[other_sw][sw][1]
    return local_mac, remote_mac


def emitter_for_next_hop(sw: str, next_node: str) -> Tuple[int, str, str]:
    port, src_mac = SWITCH_PORTS[sw][next_node]
    if next_node.startswith("h"):
        dst_mac = HOST_MAC[next_node]
    else:
        _, dst_mac = SWITCH_PORTS[next_node][sw]
    return port, src_mac, dst_mac


def emitter_for_prev_hop(sw: str, prev_node: str) -> Tuple[int, str, str]:
    if prev_node.startswith("h"):
        port = SWITCH_PORTS[sw][prev_node][0]
        src_mac = host_downlink_src_mac(prev_node)
        dst_mac = HOST_MAC[prev_node]
        return port, src_mac, dst_mac
    port, src_mac = SWITCH_PORTS[sw][prev_node]
    _, dst_mac = SWITCH_PORTS[prev_node][sw]
    return port, src_mac, dst_mac


def unique(lines: List[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for line in lines:
        if line not in seen:
            seen.add(line)
            out.append(line)
    return out


def generate_rules(
    jobs: List[Job],
    agg_map: Dict[int, str],
    tapina_switches: Set[str],
    normal_switches: Set[str],
) -> Dict[str, object]:
    tb_forward: Dict[str, List[str]] = defaultdict(list)
    receive_udp: Dict[str, List[str]] = defaultdict(list)
    dst_addr: Dict[str, List[str]] = defaultdict(list)
    tb_set_eth: Dict[str, List[str]] = defaultdict(list)
    forward: Dict[str, List[str]] = defaultdict(list)
    multicast_groups: Dict[int, List[str]] = defaultdict(list)

    for job in jobs:
        agg = agg_map[job.job_id]
        multicast_groups[job.job_id] = list(job.workers)
        forward[agg].append(f"(1,{sw_num(agg)},{job.job_id},_,1,_) : flood({job.job_id}); // agg={agg}")

    for job in jobs:
        agg = agg_map[job.job_id]
        worker_index = bitmap_order(job.workers)
        num_workers = len(job.workers)

        for worker in job.workers:
            wid = host_num(worker)
            src_ip_hex = ip_to_hex(HOST_IP[worker])
            bitpos = worker_index[worker]
            worker_bitmap = f"1<<{bitpos}" if bitpos > 0 else "1"

            receive_udp[agg].append(
                f"(_, _, _, {src_ip_hex}, _, 48864, {job.job_id}, {sw_num(agg)}) : set_bitmap({job.job_id}, {wid}, {num_workers}, {worker_bitmap}, 1);"
            )
            for tap_sw in sorted(tapina_switches, key=sw_num):
                if tap_sw == agg:
                    continue
                receive_udp[tap_sw].append(
                    f"(_, _, _, {src_ip_hex}, _, 48864, {job.job_id}, {sw_num(tap_sw)}) : set_bitmap({job.job_id}, {wid}, {num_workers}, {worker_bitmap}, 0);"
                )

            path_nodes = full_worker_path(worker, agg)
            tor_to_agg = path_nodes[1:]

            rev_nodes = list(reversed(path_nodes))
            first_downstream = rev_nodes[1]
            if first_downstream.startswith("h"):
                src_mac = host_downlink_src_mac(worker)
                dst_mac = HOST_MAC[worker]
            else:
                src_mac, dst_mac = switch_link_macs(agg, first_downstream)
            dst_addr[agg].append(
                f"{format_dst_addr_key(job.job_id, wid)} : {set_dst_addr_line(src_mac, dst_mac, worker, comment=f'{worker} via {agg}->{first_downstream}') }"
            )

            for sw in tor_to_agg:
                if sw == agg:
                    continue
                prev_node, next_node = next_and_prev_switch_nodes(path_nodes, sw)
                if prev_node is None or next_node is None:
                    raise RuntimeError(f"잘못된 경로 해석: {path_nodes}")

                up_port, up_src_mac, up_dst_mac = emitter_for_next_hop(sw, next_node)
                down_port, down_src_mac, down_dst_mac = emitter_for_prev_hop(sw, prev_node)
                comment_base = f"job {job.job_id}, src {worker}, path {'->'.join(tor_to_agg)}"

                if sw in normal_switches:
                    tb_forward[sw].append(
                        f"(_, {job.job_id}, 0, {src_ip_hex}) : {set_egress_line(up_port, up_dst_mac, up_src_mac, comment=comment_base + ', uplink')}"
                    )
                    tb_forward[sw].append(
                        f"(_, {job.job_id}, 1, {src_ip_hex}) : {set_egress_line(down_port, down_dst_mac, down_src_mac, comment=comment_base + ', downlink')}"
                    )
                elif sw in tapina_switches:
                    forward[sw].append(
                        f"(0,{sw_num(sw)},{job.job_id},_,0,{wid}) : set_egress_port({up_port}); // {comment_base}, uplink"
                    )
                    forward[sw].append(
                        f"(0,{sw_num(sw)},{job.job_id},_,1,{wid}) : set_egress_port({down_port}); // {comment_base}, downlink"
                    )
                    tb_set_eth[sw].append(
                        f"(0,{sw_num(sw)},{job.job_id},4,0,{wid}) : {set_adder_line(up_src_mac, up_dst_mac, comment=comment_base + ', uplink')}"
                    )
                    tb_set_eth[sw].append(
                        f"(0,{sw_num(sw)},{job.job_id},4,1,{wid}) : {set_adder_line(down_src_mac, down_dst_mac, comment=comment_base + ', downlink')}"
                    )
                else:
                    raise RuntimeError(f"switch role을 알 수 없습니다: {sw}")

    return {
        "tb_forward": {sw: unique(lines) for sw, lines in tb_forward.items()},
        "receive_udp": {sw: unique(lines) for sw, lines in receive_udp.items()},
        "dst_addr": {sw: unique(lines) for sw, lines in dst_addr.items()},
        "tb_set_ethernet_address": {sw: unique(lines) for sw, lines in tb_set_eth.items()},
        "forward": {sw: unique(lines) for sw, lines in forward.items()},
        "multicast_groups": multicast_groups,
    }


def build_switch_program_map(tapina_switches: Set[str]) -> Dict[str, str]:
    return {sw: ("tapina.p4" if sw in tapina_switches else f"normal_forwarding_{sw_num(sw)}.p4") for sw in ALL_SWITCHES}


def generate_agg_runtime_commands(
    jobs: List[Job],
    agg_map: Dict[int, str],
    tapina_switches: Set[str],
    sw_to_jobs: Dict[str, List[int]],
) -> Dict[str, List[str]]:
    if any(job.job_id > MAX_STATIC_JOB_ACTIONS for job in jobs):
        raise RuntimeError(
            f"현재 tapina.p4는 Job1..Job{MAX_STATIC_JOB_ACTIONS}, read_worker_job1..{MAX_STATIC_JOB_ACTIONS}까지만 정의되어 있습니다."
        )

    job_lookup = {job.job_id: job for job in jobs}
    out: Dict[str, List[str]] = {}

    for sw in sorted(tapina_switches, key=sw_num):
        lines: List[str] = []
        lines.append(f"table_add tb_set_switch_id set_switch_id 4 => {sw_num(sw)}")
        for job_id in sorted(sw_to_jobs.get(sw, [])):
            lines.append(f"table_add tb_worker_count worker_count 1 {job_id} =>")
            lines.append(f"table_add tb_set_worker_id read_worker_job{job_id} 1 {job_id} =>")

        lines.append("")
        for idx in range(MAX_STATIC_JOB_ACTIONS):
            lines.append(f"register_write MyEgress.worker_counter {idx} 0")

        lines.append("")
        for job_id in range(1, MAX_STATIC_JOB_ACTIONS + 1):
            if job_id not in job_lookup:
                continue
            job = job_lookup[job_id]
            for idx, worker in enumerate(job.workers):
                lines.append(f"register_write MyEgress.Job{job_id} {idx} {host_num(worker)}")
            lines.append("")

        lines.append("# Multicast Rules")
        node_id = 0
        for job_id in sorted(sw_to_jobs.get(sw, [])):
            job = job_lookup[job_id]
            lines.append(f"mc_mgrp_create {job_id}")
            node_ids_for_job: List[int] = []
            for worker in job.workers:
                path_nodes = full_worker_path(worker, sw)
                rev_nodes = list(reversed(path_nodes))
                if len(rev_nodes) < 2:
                    raise RuntimeError(f"잘못된 downlink 경로: {path_nodes}")
                first_downstream = rev_nodes[1]
                port = SWITCH_PORTS[sw][first_downstream][0]
                lines.append(f"mc_node_create {node_id}  {port}")
                node_ids_for_job.append(node_id)
                node_id += 1
            for nid in node_ids_for_job:
                lines.append(f"mc_node_associate {job_id} {nid}")
            lines.append("")
        out[sw] = lines

    return out


def write_outputs(
    output_dir: Path,
    jobs: List[Job],
    agg_map: Dict[int, str],
    tapina_switches: Set[str],
    normal_switches: Set[str],
    sw_to_jobs: Dict[str, List[int]],
    rules: Dict[str, object],
    agg_runtime_cmds: Dict[str, List[str]],
) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    normal_dir = output_dir / "normal"
    tapina_dir = output_dir / "tapina"
    normal_dir.mkdir(parents=True, exist_ok=True)
    tapina_dir.mkdir(parents=True, exist_ok=True)

    for sw in sorted(normal_switches, key=sw_num):
        lines = rules["tb_forward"].get(sw, [])
        (normal_dir / f"{sw}_tb_forward_entries.p4").write_text("\n".join(lines) + ("\n" if lines else ""))

    for sw in sorted(tapina_switches, key=sw_num):
        (tapina_dir / f"{sw}_receive_udp_entries.p4").write_text("\n".join(rules["receive_udp"].get(sw, [])) + ("\n" if rules["receive_udp"].get(sw) else ""))
        (tapina_dir / f"{sw}_dst_addr_entries.p4").write_text("\n".join(rules["dst_addr"].get(sw, [])) + ("\n" if rules["dst_addr"].get(sw) else ""))
        (tapina_dir / f"{sw}_tb_set_ethernet_address_entries.p4").write_text("\n".join(rules["tb_set_ethernet_address"].get(sw, [])) + ("\n" if rules["tb_set_ethernet_address"].get(sw) else ""))
        (tapina_dir / f"{sw}_forward_entries.p4").write_text("\n".join(rules["forward"].get(sw, [])) + ("\n" if rules["forward"].get(sw) else ""))
        (tapina_dir / f"{sw}_agg_runtime_commands.txt").write_text("\n".join(agg_runtime_cmds.get(sw, [])) + ("\n" if agg_runtime_cmds.get(sw) else ""))

    summary = {
        "jobs": {job.job_id: {"workers": job.workers, "model_size": job.model_size} for job in jobs},
        "agg_switch": agg_map,
        "tapina_switches": sorted(tapina_switches, key=sw_num),
        "normal_switches": sorted(normal_switches, key=sw_num),
        "switch_to_jobs": {sw: sorted(js) for sw, js in sw_to_jobs.items()},
        "switch_program_map": build_switch_program_map(tapina_switches),
        "multicast_groups": rules["multicast_groups"],
        "tapina_runtime_command_files": {sw: f"tapina/{sw}_agg_runtime_commands.txt" for sw in sorted(tapina_switches, key=sw_num)},
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2))

    network_lines = [
        '# Auto-generated P4 source assignment',
        'p4_tapina = "/home/tofino/TAPINA/p4src/tapina.p4"',
    ]
    for sw in ALL_SWITCHES:
        if sw in normal_switches:
            network_lines.append(f'p4_forwarding_{sw_num(sw)} = "/home/tofino/TAPINA/p4src/normal_forwarding_{sw_num(sw)}.p4"')
    network_lines.append("")
    for sw in ALL_SWITCHES:
        if sw in tapina_switches:
            network_lines.append(f'net.setP4Source("{sw}", p4_tapina)')
        else:
            network_lines.append(f'net.setP4Source("{sw}", p4_forwarding_{sw_num(sw)})')
    (output_dir / "network_setP4Source_snippet.py").write_text("\n".join(network_lines) + "\n")


def generate_apps(num: int, hosts: List[str]) -> List[List[object]]:
    apps = []
    while len(apps) < num:
        random.shuffle(hosts)
        worker_num = np.random.randint(3, 7)
        model_size = np.random.randint(1, 20)
        app = [hosts[0:worker_num], model_size]
        if app not in apps:
            apps.append(app)
    return apps


def jobs_from_apps(apps: List[List[object]]) -> List[Job]:
    return [Job(idx, [w.lower() for w in workers], int(model_size)) for idx, (workers, model_size) in enumerate(apps, start=1)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate TAPINA/normal_forwarding rules aligned with the current uploaded repo rules.")
    parser.add_argument("--jobs-json", type=Path, help="JSON file with jobs and optional placement params")
    parser.add_argument("--k", type=int, default=3, help="Maximum number of selected TAPINA switches")
    parser.add_argument("--capacity", type=int, default=2, help="Maximum number of jobs per selected TAPINA switch")
    parser.add_argument("--ps-attach-switch", type=str, default="s8", help="Virtual PS attach switch used by functions_.py selection cost")
    parser.add_argument("--output-dir", type=Path, default=Path("generated_rules_dynamic"))
    parser.add_argument("--app-num", type=int, default=5)
    args = parser.parse_args()

    manual_agg: Dict[int, str] = {}
    if args.jobs_json:
        jobs, placement_cfg, manual_agg = jobs_from_json(args.jobs_json)
        args.k = int(placement_cfg.get("k", args.k))
        args.capacity = int(placement_cfg.get("capacity", args.capacity))
        args.ps_attach_switch = str(placement_cfg.get("ps_attach_switch", args.ps_attach_switch)).lower()
    else:
        apps = generate_apps(args.app_num, [f"h{i}" for i in range(1, 13)])
        jobs = jobs_from_apps(apps)

    if manual_agg:
        agg_map, tapina_switches, normal_switches, sw_to_jobs = derive_manual_solution(
            jobs=jobs,
            agg_map=manual_agg,
            k=args.k,
            capacity=args.capacity,
        )
    else:
        agg_map, tapina_switches, normal_switches, sw_to_jobs = derive_matching_solution(
            jobs=jobs,
            k=args.k,
            capacity=args.capacity,
            ps_attach_switch=args.ps_attach_switch,
            candidate_switches=ALL_SWITCHES_UPPER,
        )

    rules = generate_rules(jobs, agg_map, tapina_switches, normal_switches)
    agg_runtime_cmds = generate_agg_runtime_commands(jobs, agg_map, tapina_switches, sw_to_jobs)
    write_outputs(args.output_dir, jobs, agg_map, tapina_switches, normal_switches, sw_to_jobs, rules, agg_runtime_cmds)

    print("[DONE] dynamic rule generation completed")
    print("selected TAPINA switches:", sorted(tapina_switches, key=sw_num))
    print("selected normal switches:", sorted(normal_switches, key=sw_num))
    print("agg_map:", {k: agg_map[k] for k in sorted(agg_map)})
    print("output_dir:", args.output_dir)


if __name__ == "__main__":
    main()
