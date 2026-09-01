from sklearn.ensemble import IsolationForest
import joblib
from pathlib import Path
import numpy as np

def train_isolation_forest(X, out_dir, n_estimators=100, contamination=0.01):
    clf = IsolationForest(n_estimators=n_estimators, contamination=contamination, random_state=42)
    clf.fit(X)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, out_dir / 'isolation_forest.joblib')
    return clf


def load_isolation_forest(path):
    return joblib.load(path)


# Simple autoencoder using TensorFlow Keras
def build_autoencoder(input_dim, latent_dim=8):
    try:
        from tensorflow import keras
    except Exception:
        raise
    inputs = keras.Input(shape=(input_dim,))
    x = keras.layers.Dense(max(32, input_dim * 2), activation='relu')(inputs)
    x = keras.layers.Dense(latent_dim, activation='relu')(x)
    x = keras.layers.Dense(max(32, input_dim * 2), activation='relu')(x)
    outputs = keras.layers.Dense(input_dim, activation='linear')(x)
    model = keras.Model(inputs, outputs, name='autoencoder')
    model.compile(optimizer='adam', loss='mse')
    return model


def train_autoencoder(X, out_dir, epochs=20, batch_size=64):
    from tensorflow import keras
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    model = build_autoencoder(X.shape[1])
    model.fit(X, X, epochs=epochs, batch_size=batch_size, validation_split=0.1, verbose=1)
    model.save(out_dir / 'autoencoder')
    return model


def load_autoencoder(path):
    from tensorflow import keras
    return keras.models.load_model(path)


def reconstruction_errors(model, X):
    preds = model.predict(X)
    err = np.mean((preds - X) ** 2, axis=1)
    return err


# Fallback autoencoder using scikit-learn's MLPRegressor when TensorFlow is unavailable
def train_sklearn_autoencoder(X, out_dir, hidden_layer_sizes=(64, 16, 64), max_iter=200):
    from sklearn.neural_network import MLPRegressor
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ae = MLPRegressor(hidden_layer_sizes=hidden_layer_sizes, activation='relu', solver='adam', max_iter=max_iter, random_state=42)
    # Train to reconstruct input
    ae.fit(X, X)
    joblib.dump(ae, out_dir / 'autoencoder_sklearn.joblib')
    return ae


def load_sklearn_autoencoder(path):
    return joblib.load(path)


def reconstruction_errors_sklearn(model, X):
    preds = model.predict(X)
    err = np.mean((preds - X) ** 2, axis=1)
    return err
