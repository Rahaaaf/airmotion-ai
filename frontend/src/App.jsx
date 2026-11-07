import { useEffect, useState } from "react";
import {
  Activity,
  BrainCircuit,
  Radio,
  Zap,
  RefreshCw,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  RotateCw,
  Waves,
} from "lucide-react";

const API = "";
const GESTURES = ["UP", "DOWN", "LEFT", "RIGHT", "CIRCLE", "SHAKE", "UNKNOWN"];
const ACTIONS = [
  "SCROLL_UP",
  "SCROLL_DOWN",
  "GO_BACK",
  "GO_FORWARD",
  "NEW_TAB",
  "CLOSE_TAB",
  "RELOAD_PAGE",
  "NONE",
];

const ICONS = {
  UP: ArrowUp,
  DOWN: ArrowDown,
  LEFT: ArrowLeft,
  RIGHT: ArrowRight,
  CIRCLE: RotateCw,
  SHAKE: Waves,
  UNKNOWN: Activity,
};

export default function App() {
  const [status, setStatus] = useState(null);
  const [events, setEvents] = useState([]);
  const [mappings, setMappings] = useState({});
  const [latest, setLatest] = useState(null);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);

  async function api(path, options = {}) {
    const response = await fetch(API + path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "API request failed");
    }

    return response.json();
  }

  async function refresh() {
    try {
      const [s, e, m] = await Promise.all([
        api("/api/status"),
        api("/api/events?limit=100"),
        api("/api/mappings"),
      ]);

      setStatus(s);
      setEvents(e);
      setMappings(m);
    } catch (error) {
      console.error(error);
    }
  }

  useEffect(() => {
    refresh();

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const socket = new WebSocket(`${protocol}//${window.location.host}/ws/studio`);

    socket.onopen = () => setConnected(true);
    socket.onclose = () => setConnected(false);

    socket.onmessage = (message) => {
      const event = JSON.parse(message.data);
      if (event.gesture_id) {
        setLatest(event);
        refresh();
      }
    };

    return () => socket.close();
  }, []);

  async function runDemo() {
    setLoading(true);
    try {
      const result = await api("/api/demo", { method: "POST" });
      setLatest(result);
      await refresh();
    } catch (error) {
      alert(error.message);
    }
    setLoading(false);
  }

  function updateMapping(gesture, action) {
    setMappings((previous) => ({ ...previous, [gesture]: action }));
  }

  async function saveMappings() {
    try {
      await api("/api/mappings", {
        method: "PUT",
        body: JSON.stringify({ mappings }),
      });
      alert("Mappings saved successfully!");
      refresh();
    } catch (error) {
      alert(error.message);
    }
  }

  const confidence = latest ? latest.confidence * 100 : 0;

  return (
    <div className="app">
      <header className="navbar">
        <div className="logo">
          <BrainCircuit size={25} />
          AirMotion <span>Studio</span>
        </div>

        <div className="connection">
          <span className={connected ? "dot online" : "dot"} />
          {connected ? "Connected" : "Disconnected"}
        </div>
      </header>

      <main>
        <section className="page-heading">
          <div>
            <h1>Gesture Intelligence</h1>
            <p>Neural Network · IMU · Browser Automation</p>
          </div>

          <button className="primary-button" onClick={runDemo} disabled={loading}>
            <Zap size={17} />
            {loading ? "Running..." : "Run NN Demo"}
          </button>
        </section>

        <section className="metrics">
          <Metric icon={<BrainCircuit />} label="Neural Network" value={status?.model_loaded ? "READY" : "OFFLINE"} />
          <Metric icon={<Activity />} label="Predictions" value={events.length} />
          <Metric icon={<Radio />} label="Last Confidence" value={latest ? `${confidence.toFixed(1)}%` : "—"} />
          <Metric icon={<Zap />} label="Navigator" value="WebSocket" />
        </section>

        <section className="main-grid">
          <div className="panel prediction-panel">
            <h2>Live Neural Network Prediction</h2>
            <p className="muted">Latest classification result</p>

            <div className="prediction-result">{latest?.gesture_id || "Waiting for prediction"}</div>

            <div className="confidence-label">
              <span>Confidence</span>
              <strong>{confidence.toFixed(1)}%</strong>
            </div>

            <div className="progress">
              <div style={{ width: `${confidence}%` }} />
            </div>

            <p className="action-result">
              Browser Action: <strong>{latest?.action_id || "NONE"}</strong>
            </p>

            <h3>Supported Gestures</h3>
            <div className="gesture-grid">
              {GESTURES.filter((gesture) => gesture !== "UNKNOWN").map((gesture) => {
                const Icon = ICONS[gesture];
                return (
                  <div className="gesture-card" key={gesture}>
                    <Icon size={25} />
                    <strong>{gesture}</strong>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="panel">
            <h2>Gesture Mapping</h2>
            <p className="muted">Configure browser actions</p>

            <div className="mapping-list">
              {GESTURES.map((gesture) => (
                <div className="mapping-row" key={gesture}>
                  <strong>{gesture}</strong>
                  <select value={mappings[gesture] || "NONE"} onChange={(e) => updateMapping(gesture, e.target.value)}>
                    {ACTIONS.map((action) => (
                      <option key={action} value={action}>
                        {action}
                      </option>
                    ))}
                  </select>
                </div>
              ))}
            </div>

            <button className="save-button" onClick={saveMappings}>Save Configuration</button>
          </div>
        </section>

        <section className="panel history-panel">
          <div className="section-heading">
            <div>
              <h2>Event History</h2>
              <p className="muted">Neural Network prediction logs</p>
            </div>

            <button onClick={refresh}>
              <RefreshCw size={16} />
              Refresh
            </button>
          </div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Gesture</th>
                  <th>Action</th>
                  <th>Confidence</th>
                  <th>Device</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {events.map((event) => (
                  <tr key={event.event_id}>
                    <td>
                      <span className="tag">{event.gesture_id}</span>
                    </td>
                    <td>{event.action_id}</td>
                    <td>{(event.confidence * 100).toFixed(1)}%</td>
                    <td>{event.device_id}</td>
                    <td>{new Date(event.detected_at).toLocaleTimeString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            {events.length === 0 && <p className="empty">No events yet. Run the NN demo.</p>}
          </div>
        </section>

        <footer>AirMotion AI · Neural Gesture Recognition</footer>
      </main>
    </div>
  );
}

function Metric({ icon, label, value }) {
  return (
    <div className="metric-card">
      <div className="metric-icon">{icon}</div>
      <p>{label}</p>
      <strong>{value}</strong>
    </div>
  );
}
