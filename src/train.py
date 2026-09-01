
import argparse
from pathlib import Path
from src import features, models
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', required=True, help='Path to CSV with traffic features')
    parser.add_argument('--out', required=True, help='Output directory to store models')
    parser.add_argument('--epochs', type=int, default=20)
    parser.add_argument('--contamination', type=float, default=0.01)
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = features.load_csv(args.csv)
    X, cols = features.extract_features(df)
    scaler, Xs = features.fit_scaler(X, out_dir)

    print('Training IsolationForest...')
    models.train_isolation_forest(Xs, out_dir, contamination=args.contamination)

    print('Training Autoencoder (if available)...')
    try:
        models.train_autoencoder(Xs, out_dir, epochs=args.epochs)
    except Exception as e:
        print('Autoencoder training failed or TensorFlow missing:', e)
        print('Falling back to scikit-learn MLP autoencoder...')
        models.train_sklearn_autoencoder(Xs, out_dir, max_iter=200)

    print('Models saved to', out_dir)


if __name__ == '__main__':
    main()

# your-command > workspace\terminal_output.txt 2>&1
