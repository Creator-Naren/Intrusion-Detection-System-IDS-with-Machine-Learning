"""Export packet-level CSV from a pcap using tshark.

Requires `tshark` on the PATH. Writes a CSV with columns:
time,protocol,tcp_srcport,tcp_dstport,udp_srcport,udp_dstport,src_ip,dst_ip,length,tcp_flags
"""
import subprocess
import argparse
from pathlib import Path


def check_tshark():
    try:
        subprocess.run(['tshark', '-v'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def pcap_to_csv(pcap_path, out_csv):
    if not check_tshark():
        raise RuntimeError('tshark not found on PATH. Install Wireshark/tshark to use this script')

    fields = [
        'frame.time_epoch',
        'ip.proto',
        'tcp.srcport',
        'tcp.dstport',
        'udp.srcport',
        'udp.dstport',
        'ip.src',
        'ip.dst',
        'frame.len',
        'tcp.flags'
    ]
    cmd = [
        'tshark', '-r', str(pcap_path), '-T', 'fields', '-E', 'header=y', '-E', 'separator=,',
    ]
    for f in fields:
        cmd += ['-e', f]

    with open(out_csv, 'w', encoding='utf-8') as fo:
        subprocess.run(cmd, stdout=fo)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pcap', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    pcap_to_csv(args.pcap, args.out)


if __name__ == '__main__':
    main()
