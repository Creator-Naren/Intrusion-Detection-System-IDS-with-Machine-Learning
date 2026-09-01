Intrusion Detection System (IDS) with Machine Learning

Overview
- Minimal IDS prototype that uses feature-based traffic data to train two detectors:
  - IsolationForest (scikit-learn) for unsupervised anomaly detection
  - Autoencoder (TensorFlow) for reconstruction-based anomaly detection

Quickstart
1. Create a Python environment and install dependencies:

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\pip install -r requirements.txt
```

2. Generate sample data and train:

```bash
python src/train.py --csv data/sample_traffic.csv --out models/
```

3. Run detector on new CSV:

```bash
python src/detect.py --csv data/sample_traffic.csv --models models/
```

Using real captures
- Use `tshark` / Wireshark to export flows or simple CSV with fields: duration, protocol, src_bytes, dst_bytes, packets, flags
- You can adapt `src/features.py` to parse pcap files with `pyshark` or `scapy`.

Files
- src/features.py
- src/models.py
- src/train.py
- src/detect.py
- data/sample_traffic.csv

License
- MIT (use as a learning project)
