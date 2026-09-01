"""Aggregate packet CSV into flow-level CSV.

Input packet CSV columns expected: time,protocol,tcp_srcport,tcp_dstport,udp_srcport,udp_dstport,src_ip,dst_ip,length,tcp_flags
Output flow CSV will contain: duration,protocol,src_bytes,dst_bytes,packets,flags,src_port,dst_port,src_ip,dst_ip,mean_pkt_size,pkt_per_sec,total_bytes
"""
import pandas as pd
import argparse
from pathlib import Path


def pick_port(row):
    # prefer tcp ports if present else udp
    if pd.notna(row['tcp_srcport']) and row['tcp_srcport'] != '':
        return int(row['tcp_srcport']), int(row['tcp_dstport']) if pd.notna(row['tcp_dstport']) and row['tcp_dstport'] != '' else 0
    if pd.notna(row['udp_srcport']) and row['udp_srcport'] != '':
        return int(row['udp_srcport']), int(row['udp_dstport']) if pd.notna(row['udp_dstport']) and row['udp_dstport'] != '' else 0
    return 0, 0


def aggregate(packet_csv, out_csv):
    df = pd.read_csv(packet_csv)
    # normalize columns
    for c in ['tcp_srcport','tcp_dstport','udp_srcport','udp_dstport','ip.src','ip.dst','ip.proto','frame.time_epoch','frame.len','tcp.flags']:
        if c not in df.columns:
            df[c] = None

    # rename for readability if tshark header different
    # ensure expected column names
    if 'frame.time_epoch' in df.columns:
        df = df.rename(columns={'frame.time_epoch':'time'})
    if 'ip.proto' in df.columns:
        df = df.rename(columns={'ip.proto':'protocol'})
    if 'ip.src' in df.columns:
        df = df.rename(columns={'ip.src':'src_ip'})
    if 'ip.dst' in df.columns:
        df = df.rename(columns={'ip.dst':'dst_ip'})
    if 'frame.len' in df.columns:
        df = df.rename(columns={'frame.len':'length'})
    if 'tcp.flags' in df.columns:
        df = df.rename(columns={'tcp.flags':'tcp_flags'})

    # fill types
    df['time'] = pd.to_numeric(df['time'], errors='coerce').fillna(0)
    df['length'] = pd.to_numeric(df['length'], errors='coerce').fillna(0).astype(int)
    df['protocol'] = pd.to_numeric(df['protocol'], errors='coerce').fillna(0).astype(int)

    # extract ports
    ports = df.apply(lambda r: pick_port(r), axis=1)
    df['src_port'] = [p[0] for p in ports]
    df['dst_port'] = [p[1] for p in ports]

    # group by 5-tuple
    g = df.groupby(['src_ip','dst_ip','protocol','src_port','dst_port'])
    flows = []
    for k, grp in g:
        src_ip, dst_ip, proto, src_port, dst_port = k
        times = grp['time']
        duration = times.max() - times.min() if len(times) > 1 else 0.0
        packets = len(grp)
        # credit bytes depending on packet direction
        src_bytes = grp[grp['src_ip'] == src_ip]['length'].sum()
        dst_bytes = grp[grp['src_ip'] != src_ip]['length'].sum()
        flags_val = 0
        try:
            flags_val = grp['tcp_flags'].dropna().astype(int).max() if 'tcp_flags' in grp.columns else 0
        except Exception:
            flags_val = 0
        total_bytes = int(src_bytes + dst_bytes)
        mean_pkt_size = (total_bytes / packets) if packets > 0 else 0
        pkt_per_sec = (packets / duration) if duration > 0 else packets
        flows.append({
            'duration': duration,
            'protocol': proto,
            'src_bytes': int(src_bytes),
            'dst_bytes': int(dst_bytes),
            'packets': int(packets),
            'flags': int(flags_val),
            'src_port': int(src_port),
            'dst_port': int(dst_port),
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'mean_pkt_size': mean_pkt_size,
            'pkt_per_sec': pkt_per_sec,
            'total_bytes': total_bytes
        })

    out = pd.DataFrame(flows)
    out.to_csv(out_csv, index=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--packets', required=True, help='Packet CSV from tshark')
    parser.add_argument('--out', required=True, help='Output flow CSV')
    args = parser.parse_args()
    aggregate(args.packets, args.out)


if __name__ == '__main__':
    main()
