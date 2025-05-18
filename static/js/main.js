const statusText = document.getElementById("statusText");
const toggleBtn = document.getElementById("toggleBtn");
const loggContainer = document.getElementById("logg");

async function updateStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();

    statusText.textContent = data.status === "open" ? "Åpen" : "Lukket";
    statusText.style.color = data.status === "open" ? "green" : "red";

    toggleBtn.textContent = data.status === "open" ? "Lukk port" : "Åpne port";
    toggleBtn.onclick = () => sendCommand(data.status === "open" ? "close" : "open");
  } catch (err) {
    statusText.textContent = "Feil ved henting av status";
    statusText.style.color = "orange";
    console.error(err);
  }
}

async function sendCommand(action) {
  try {
    await fetch(`/api/${action}`, { method: "POST" });
    updateStatus();
    updateLogg();
  } catch (err) {
    alert("Kommando mislyktes");
    console.error(err);
  }
}
async function updateLogg() {
  try {
    const res = await fetch("/api/logs/event");
    const data = await res.json();

    if (data.error || !data.lines) {
      loggContainer.textContent = "Logg ikke tilgjengelig.";
      return;
    }

    loggContainer.innerHTML = "";
    data.lines.forEach(line => {
      const el = document.createElement("p");
      el.textContent = line.trim();
      loggContainer.appendChild(el);
    });
  } catch (err) {
    loggContainer.textContent = "Feil ved henting av logg.";
    console.error(err);
  }
}

updateStatus();
updateLogg();
