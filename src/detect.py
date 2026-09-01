import argparse
from pathlib import Path
from src import features, models
import numpy as np
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', required=True, help='Path to CSV to analyze')
    parser.add_argument('--models', required=True, help='Directory containing trained models')
    parser.add_argument('--out', help='Optional output CSV for anomalies')
    args = parser.parse_args()

    model_dir = Path(args.models)
    df = features.load_csv(args.csv)
    X, cols = features.extract_features(df)

    scaler = features.load_scaler(model_dir / 'scaler.joblib')
    Xs = features.transform_with_scaler(X, scaler)

    iso = models.load_isolation_forest(model_dir / 'isolation_forest.joblib')
    try:
        ae = models.load_autoencoder(model_dir / 'autoencoder')
    except Exception:
        ae = None

    iso_scores = iso.decision_function(Xs)  # higher is normal in sklearn
    iso_pred = iso.predict(Xs)  # -1 anomaly, 1 normal

    if ae is not None:
        rec_err = models.reconstruction_errors(ae, Xs)
    else:
        rec_err = np.zeros(len(Xs))

    out = df.copy()
    out['iso_score'] = iso_scores
    out['iso_pred'] = iso_pred
    out['rec_err'] = rec_err

    anomalies = out[(out['iso_pred'] == -1) | (out['rec_err'] > np.percentile(out['rec_err'], 95))]

    print(f'Found {len(anomalies)} anomalies')
    if args.out:
        anomalies.to_csv(args.out, index=False)
        print('Anomalies written to', args.out)
    else:
        print(anomalies.head(50).to_string(index=False))


if __name__ == '__main__':
    main()
