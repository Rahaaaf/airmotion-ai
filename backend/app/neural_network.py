import numpy as np
import tensorflow as tf
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE / "model" / "artifacts" / "gesture_model.keras"
CLASSES_PATH = BASE / "model" / "artifacts" / "classes.npy"


class GestureRecognizer:
    def __init__(self):
        if not MODEL_PATH.exists():
            raise FileNotFoundError("Train the Neural Network first.")

        self.model = tf.keras.models.load_model(MODEL_PATH)
        self.classes = np.load(CLASSES_PATH, allow_pickle=False).tolist()

    def predict(self, window):
        data = np.asarray(window, dtype=np.float32)
        if data.shape != (50, 6):
            raise ValueError("Expected shape (50, 6)")

        probabilities = self.model.predict(data[np.newaxis, ...], verbose=0)[0]
        index = int(np.argmax(probabilities))
        gesture_id = self.classes[index]
        confidence = float(probabilities[index])

        return {
            "gesture_id": gesture_id,
            "confidence": confidence,
            "probabilities": probabilities.tolist(),
        }
