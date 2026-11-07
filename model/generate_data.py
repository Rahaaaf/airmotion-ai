import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent
WINDOW_SIZE = 50
FEATURES = 6
GESTURES = ["UP", "DOWN", "LEFT", "RIGHT", "CIRCLE", "SHAKE", "UNKNOWN"]
SAMPLES_PER_GESTURE = 500

rng = np.random.default_rng(42)


def generate_window(gesture):
    t = np.linspace(0, 1, WINDOW_SIZE)
    x = np.zeros((WINDOW_SIZE, FEATURES), dtype=np.float32)
    x[:, 2] = 9.81
    amplitude = rng.uniform(1.5, 3.5)
    phase = rng.uniform(0, 2 * np.pi)

    if gesture == "UP":
        x[:, 2] += amplitude * np.sin(np.pi * t)
        x[:, 4] = 70 * np.sin(np.pi * t + phase)
    elif gesture == "DOWN":
        x[:, 2] -= amplitude * np.sin(np.pi * t)
        x[:, 4] = -70 * np.sin(np.pi * t + phase)
    elif gesture == "LEFT":
        x[:, 0] -= amplitude * np.sin(np.pi * t)
        x[:, 3] = -65 * np.sin(np.pi * t + phase)
    elif gesture == "RIGHT":
        x[:, 0] += amplitude * np.sin(np.pi * t)
        x[:, 3] = 65 * np.sin(np.pi * t + phase)
    elif gesture == "CIRCLE":
        x[:, 0] = amplitude * np.sin(2 * np.pi * t)
        x[:, 1] = amplitude * np.cos(2 * np.pi * t)
        x[:, 3] = 60 * np.sin(2 * np.pi * t + phase)
        x[:, 4] = 60 * np.cos(2 * np.pi * t + phase)
    elif gesture == "SHAKE":
        x[:, 0] += amplitude * np.sin(2 * np.pi * 4 * t)
        x[:, 1] += amplitude * np.cos(2 * np.pi * 4 * t)
        x[:, 5] = 90 * np.sin(2 * np.pi * 8 * t)
    elif gesture == "UNKNOWN":
        x += rng.normal(0, 0.8, size=x.shape)
        x[:, 2] += rng.normal(0, 1.0, size=WINDOW_SIZE)

    x[:, 0] += rng.normal(0, 0.05, size=WINDOW_SIZE)
    x[:, 1] += rng.normal(0, 0.05, size=WINDOW_SIZE)
    x[:, 3] += rng.normal(0, 2.0, size=WINDOW_SIZE)
    x[:, 4] += rng.normal(0, 2.0, size=WINDOW_SIZE)
    x[:, 5] += rng.normal(0, 2.0, size=WINDOW_SIZE)
    return x


def build_dataset():
    X = []
    y = []

    for gesture in GESTURES:
        for _ in range(SAMPLES_PER_GESTURE):
            X.append(generate_window(gesture))
            y.append(gesture)

    X = np.asarray(X, dtype=np.float32)
    y = np.asarray(y)

    return X, y


def main():
    X, y = build_dataset()
    artifacts_dir = BASE / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)

    np.savez(
        artifacts_dir / "training_data.npz",
        X=X,
        y=y,
        classes=np.asarray(GESTURES, dtype=object),
    )

    print(f"X shape: {X.shape}")
    print(f"y shape: {y.shape}")
    print(f"Saved to: {artifacts_dir / 'training_data.npz'}")


if __name__ == "__main__":
    main()
