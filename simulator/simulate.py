import time

import numpy as np
import requests

API = "http://127.0.0.1:8000/api/predict"
GESTURES = ["UP", "DOWN", "LEFT", "RIGHT", "CIRCLE", "SHAKE", "UNKNOWN"]


def create_window(gesture):
    t = np.linspace(0, 1, 50)
    x = np.zeros((50, 6), dtype=np.float32)
    x[:, 2] = 9.81
    amplitude = 2.5

    if gesture == "UP":
        x[:, 2] += amplitude * np.sin(np.pi * t)
        x[:, 4] = 70 * np.sin(np.pi * t)
    elif gesture == "DOWN":
        x[:, 2] -= amplitude * np.sin(np.pi * t)
        x[:, 4] = -70 * np.sin(np.pi * t)
    elif gesture == "LEFT":
        x[:, 0] -= amplitude * np.sin(np.pi * t)
        x[:, 3] = -65 * np.sin(np.pi * t)
    elif gesture == "RIGHT":
        x[:, 0] += amplitude * np.sin(np.pi * t)
        x[:, 3] = 65 * np.sin(np.pi * t)
    elif gesture == "CIRCLE":
        x[:, 0] = amplitude * np.sin(2 * np.pi * t)
        x[:, 1] = amplitude * np.cos(2 * np.pi * t)
    elif gesture == "SHAKE":
        x[:, 0] += amplitude * np.sin(2 * np.pi * 4 * t)
        x[:, 1] += amplitude * np.cos(2 * np.pi * 4 * t)
    elif gesture == "UNKNOWN":
        x += np.random.default_rng(42).normal(0, 0.8, size=x.shape)

    return x.tolist()


def main():
    while True:
        gesture = np.random.choice(GESTURES)
        payload = {"window": create_window(gesture), "device_id": "simulator"}
        try:
            response = requests.post(API, json=payload, timeout=10)
            print(f"{gesture} -> {response.status_code}: {response.json()}")
        except Exception as exc:
            print(f"Request failed: {exc}")
        time.sleep(1)


if __name__ == "__main__":
    main()
