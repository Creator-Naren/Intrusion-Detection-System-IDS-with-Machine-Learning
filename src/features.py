import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path


def load_csv(path):
    df = pd.read_csv(path)
    return df


def extract_features(df):
    # Canonical flow columns we accept (optional additional features will be derived)
    base_cols = ['duration', 'protocol', 'src_bytes', 'dst_bytes', 'packets', 'flags']
    present = {c for c in df.columns}

    # Ensure required numeric columns exist; fill missing with zeros
    for c in base_cols:
        if c not in df.columns:
            df[c] = 0

    # Derived features
    df['total_bytes'] = df['src_bytes'].fillna(0) + df['dst_bytes'].fillna(0)
    # ratio src/dst (avoid div by zero)
    df['ratio_src_dst'] = df.apply(lambda r: (r['src_bytes'] / r['dst_bytes']) if r['dst_bytes'] > 0 else r['src_bytes'], axis=1)
    # packets per second
    df['pkt_per_sec'] = df.apply(lambda r: (r['packets'] / r['duration']) if r['duration'] > 0 else r['packets'], axis=1)
    # mean packet size
    df['mean_pkt_size'] = df.apply(lambda r: (r['total_bytes'] / r['packets']) if r['packets'] > 0 else r['total_bytes'], axis=1)
    # protocol flags: TCP/UDP booleans
    if 'protocol' in df.columns:
        df['is_tcp'] = df['protocol'].astype(float).fillna(0).apply(lambda p: 1.0 if int(p) == 6 else 0.0)
        df['is_udp'] = df['protocol'].astype(float).fillna(0).apply(lambda p: 1.0 if int(p) == 17 else 0.0)

    # Select features to use for ML (numeric)
    use_cols = ['duration', 'protocol', 'src_bytes', 'dst_bytes', 'packets', 'flags', 'total_bytes', 'ratio_src_dst', 'pkt_per_sec', 'mean_pkt_size', 'is_tcp', 'is_udp']
    cols = [c for c in use_cols if c in df.columns]
    X = df[cols].fillna(0).astype(float).values
    return X, cols


def fit_scaler(X, out_dir):
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, out_dir / 'scaler.joblib')
    return scaler, Xs


def load_scaler(path):
    return joblib.load(path)


def transform_with_scaler(X, scaler):
    return scaler.transform(X)


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python src/features.py data.csv')
        sys.exit(1)
    df = load_csv(sys.argv[1])
    X, cols = extract_features(df)
    print('Extracted columns:', cols)
    print('Shape:', X.shape)
