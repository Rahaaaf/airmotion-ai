let socket = null;

function connect() {
  if (socket && socket.readyState === WebSocket.OPEN) {
    return;
  }

  socket = new WebSocket("ws://127.0.0.1:8000/ws/navigator");

  socket.onopen = () => {
    console.log("AirMotion Navigator connected");
  };

  socket.onclose = () => {
    console.log("AirMotion disconnected");
    socket = null;
  };

  socket.onerror = (error) => {
    console.error("WebSocket error:", error);
  };

  socket.onmessage = (message) => {
    const event = JSON.parse(message.data);
    if (event.action_id) {
      executeAction(event.action_id);
    }
  };
}

async function executeAction(action) {
  const tabs = await chrome.tabs.query({
    active: true,
    lastFocusedWindow: true,
  });

  const tab = tabs[0];
  if (!tab?.id) return;

  try {
    switch (action) {
      case "SCROLL_UP":
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          func: () => window.scrollBy({ top: -600, behavior: "smooth" }),
        });
        break;

      case "SCROLL_DOWN":
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          func: () => window.scrollBy({ top: 600, behavior: "smooth" }),
        });
        break;

      case "GO_BACK":
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          func: () => history.back(),
        });
        break;

      case "GO_FORWARD":
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          func: () => history.forward(),
        });
        break;

      case "NEW_TAB":
        await chrome.tabs.create({});
        break;

      case "CLOSE_TAB":
        await chrome.tabs.remove(tab.id);
        break;

      case "RELOAD_PAGE":
        await chrome.tabs.reload(tab.id);
        break;

      default:
        console.log("No browser action:", action);
    }
  } catch (error) {
    console.error("Could not execute browser action:", error);
  }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "CONNECT") {
    connect();
    sendResponse({ ok: true });
  }
});
