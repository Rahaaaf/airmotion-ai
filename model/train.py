import numpy as np
import tensorflow as tf
from pathlib import Path
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

BASE = Path(__file__).resolve().parent
DATA_PATH = BASE / "artifacts" / "training_data.npz"
MODEL_PATH = BASE / "artifacts" / "gesture_model.keras"
CLASSES_PATH = BASE / "artifacts" / "classes.npy"

if not DATA_PATH.exists():
    raise FileNotFoundError("Run generate_data.py before training.")


def main():
    data = np.load(DATA_PATH)
    X = data["X"]
    y = data["y"]
    classes = data["classes"].tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    normalizer = tf.keras.layers.Normalization(axis=-1)
    normalizer.adapt(X_train)

    model = tf.keras.Sequential([
        tf.keras.Input(shape=(50, 6)),
        normalizer,
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(len(classes), activation="softmax"),
    ])

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    history = model.fit(
        X_train,
        y_train,
        validation_split=0.1,
        epochs=12,
        batch_size=64,
        verbose=1,
    )

    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test accuracy: {test_acc:.4f}")

    predictions = model.predict(X_test, verbose=0)
    predicted_labels = np.argmax(predictions, axis=1)
    y_true = np.array([classes.index(label) for label in y_test])
    print(classification_report(y_true, predicted_labels, target_names=classes))

    MODEL_PATH.parent.mkdir(exist_ok=True, parents=True)
    model.save(MODEL_PATH)
    np.save(CLASSES_PATH, np.asarray(classes, dtype=object))

    print(f"Model saved to: {MODEL_PATH}")
    print(f"Classes saved to: {CLASSES_PATH}")


if __name__ == "__main__":
    main()
