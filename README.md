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

Example output
Below are example console outputs from a training run and a detection run using the included sample data. These are meant to make it easier to see what the scripts print and what to expect when you run them.

Training (python src/train.py --csv data/sample_traffic.csv --out models/)

```text
[INFO] Loading data from data/sample_traffic.csv (1000 rows)
[INFO] Preprocessing features: ['duration', 'protocol', 'src_bytes', 'dst_bytes', 'packets', 'flags']
[INFO] Training IsolationForest...
[INFO] IsolationForest trained. Anomaly score stats: min=-0.52 mean=-0.01 max=0.67
[INFO] Training autoencoder (TensorFlow)...
Epoch 1/50 - loss: 0.0243 - val_loss: 0.0238
Epoch 10/50 - loss: 0.0101 - val_loss: 0.0105
Epoch 20/50 - loss: 0.0068 - val_loss: 0.0072
Epoch 50/50 - loss: 0.0042 - val_loss: 0.0045
[INFO] Autoencoder training complete.
[INFO] Saving models to models/
Saved: models/isolation_forest.pkl
Saved: models/autoencoder.h5
[INFO] Training finished. Summary:
 - rows: 1000
 - anomalies (IsolationForest heuristic threshold): 12 (1.2%)
 - reconstruction-based anomalies (autoencoder, threshold): 15 (1.5%)
```

Detection (python src/detect.py --csv data/sample_traffic.csv --models models/)

```text
[INFO] Loading models from models/
[INFO] Loading 1000 rows from data/sample_traffic.csv
[INFO] Scoring with IsolationForest...
[INFO] Scoring with Autoencoder (reconstruction error)...
[INFO] Combining results and applying thresholds...
Index, duration, protocol, src_bytes, dst_bytes, packets, flags, iso_score, recon_error, flagged
42, 0.024, TCP, 200, 1500, 10, S, -0.45, 0.012, True
87, 1.230, UDP, 50, 10, 2, -, -0.30, 0.020, True
256, 0.600, TCP, 5000, 1, 25, P, 0.55, 0.001, False
...
[INFO] Detection complete. 18 unique flows flagged (1.8%)
[INFO] Detailed results saved to models/detections_2026-09-01.csv
```

Example JSON output (models/detections_2026-09-01.csv -> same data in CSV/JSON)

```json
{
  "row": 42,
  "duration": 0.024,
  "protocol": "TCP",
  "src_bytes": 200,
  "dst_bytes": 1500,
  "packets": 10,
  "flags": "S",
  "iso_score": -0.45,
  "recon_error": 0.012,
  "flagged": true
}
```

Tips for interpreting output
- iso_score: lower (more negative) usually indicates more anomalous for IsolationForest depending on implementation; check your implementation's score sign.
- recon_error: higher reconstruction error from the autoencoder indicates the sample is unlike the training set.
- Use both detectors together to reduce false positives: e.g., flag only flows detected by both, or tune thresholds to your dataset.

License
- MIT (use as a learning project)
