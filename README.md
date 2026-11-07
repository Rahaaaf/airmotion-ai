# AirMotion AI

AirMotion AI is a neural-network-based gesture control prototype for browser and device interaction.

## Architecture

- Python + TensorFlow/Keras for the gesture classifier model
- FastAPI backend with WebSocket streaming
- SQLite for event persistence
- React + Vite dashboard
- Chrome extension for browser automation
- ESP32 serial bridge for real IMU input
- Codespaces-ready setup

## Project structure

```text
airmotion-ai/
├── .devcontainer/
│   ├── devcontainer.json
│   └── setup.sh
├── model/
│   ├── generate_data.py
│   ├── train.py
│   └── artifacts/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── neural_network.py
│   │   └── airmotion.db
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       └── style.css
├── navigator/
│   ├── background.js
│   ├── manifest.json
│   ├── popup.html
│   └── popup.js
├── simulator/
│   ├── requirements.txt
│   └── simulate.py
├── bridge/
│   ├── requirements.txt
│   └── serial_bridge.py
├── .gitignore
├── LICENSE
└── README.md
```

## Quick start in GitHub Codespaces

1. Open the repository in Codespaces.
2. Start the backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Start the frontend:

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

4. Open the forwarded port for `5173` and the backend on `8000`.

## Training the model

```bash
cd model
python -m venv .venv
source .venv/bin/activate
pip install tensorflow numpy scikit-learn matplotlib
python generate_data.py
python train.py
```

## Important notes

- The first model is trained on synthetic IMU windows to validate the full pipeline.
- Real sensor data should replace the generated windows later.
- The backend loads the trained model and executes inference for incoming windows.
- The extension sends browser actions like scroll, back, forward, tab creation, and reload.

## License

MIT
