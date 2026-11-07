import argparse
import json
import time
from collections import deque

import requests
import serial

FEATURES = ["accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"]


def build_window_from_frame(frame):
    values = []
    for key in FEATURES:
        values.append(float(frame[key]))
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True)
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--server", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    frames = deque(maxlen=50)

    try:
        with serial.Serial(args.port, args.baud, timeout=1) as port:
            while True:
                line = port.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if set(FEATURES).issubset(payload.keys()):
                    frames.append(build_window_from_frame(payload))

                if len(frames) == 50:
                    response = requests.post(
                        f"{args.server}/api/predict",
                        json={"window": list(frames), "device_id": "esp32"},
                        timeout=10,
                    )
                    print(response.status_code, response.json())
                    frames.clear()
                    time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopped serial bridge.")


if __name__ == "__main__":
    main()
