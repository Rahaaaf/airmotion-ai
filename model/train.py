
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
    raise FileNotFoundError(
        "Training data not found. Run: python model/generate_data.py"
    )


def main():
    # 1. Load dataset
    with np.load(DATA_PATH, allow_pickle=False) as data:
        X = data["X"].astype(np.float32)
        y = data["y"].astype(str)
        classes = data["classes"].astype(str).tolist()

    print("Dataset loaded.")
    print("X shape:", X.shape)
    print("y shape:", y.shape)
    print("Classes:", classes)

    # 2. Convert gesture names into numerical labels
    label_to_id = {
        gesture: index
        for index, gesture in enumerate(classes)
    }

    unknown_labels = set(y) - set(classes)

    if unknown_labels:
        raise ValueError(f"Unknown gesture labels: {unknown_labels}")

    y_encoded = np.array(
        [label_to_id[label] for label in y],
        dtype=np.int32
    )

    # 3. Split training and testing data
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_encoded,
        test_size=0.2,
        random_state=42,
        stratify=y_encoded,
    )

    print("\nTraining samples:", len(X_train))
    print("Testing samples:", len(X_test))

    # 4. Normalize sensor data
    normalizer = tf.keras.layers.Normalization(axis=-1)
    normalizer.adapt(X_train)

    # 5. Build Neural Network
    model = tf.keras.Sequential([
        tf.keras.Input(shape=(50, 6)),
        normalizer,
        tf.keras.layers.Flatten(),

        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dropout(0.2),

        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dropout(0.2),

        tf.keras.layers.Dense(
            len(classes),
            activation="softmax"
        ),
    ])

    # 6. Compile model
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    model.summary()

    # 7. Train model
    print("\nStarting training...\n")

    model.fit(
        X_train,
        y_train,
        validation_split=0.1,
        epochs=12,
        batch_size=64,
        verbose=1,
    )

    # 8. Evaluate model
    test_loss, test_acc = model.evaluate(
        X_test,
        y_test,
        verbose=0
    )

    print("\nEvaluation results:")
    print(f"Test loss: {test_loss:.4f}")
    print(f"Test accuracy: {test_acc:.4f}")

    # 9. Generate predictions
    predictions = model.predict(X_test, verbose=0)

    predicted_labels = np.argmax(predictions, axis=1)

    print("\nClassification Report:\n")

    print(
        classification_report(
            y_test,
            predicted_labels,
            labels=np.arange(len(classes)),
            target_names=classes,
            zero_division=0,
        )
    )

    # 10. Save trained model and class names
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    model.save(MODEL_PATH)

    # Save as string array, not object array
    np.save(
        CLASSES_PATH,
        np.asarray(classes, dtype=str)
    )

    print("\nTraining completed successfully!")
    print("Model saved to:", MODEL_PATH)
    print("Classes saved to:", CLASSES_PATH)


if __name__ == "__main__":
    main()
