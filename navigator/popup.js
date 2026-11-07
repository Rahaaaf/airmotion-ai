const status = document.getElementById("status");

document.getElementById("connect").addEventListener("click", () => {
  chrome.runtime.sendMessage({ type: "CONNECT" }, (response) => {
    if (response?.ok) {
      status.textContent = "Connected!";
    } else {
      status.textContent = "Connection failed";
    }
  });
});
