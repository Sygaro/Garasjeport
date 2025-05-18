document.addEventListener("DOMContentLoaded", () => {
  const portStatus = document.getElementById("portStatus");
  const logList = document.getElementById("logList");
  const toggleBtn = document.getElementById("toggleBtn");

  const fetchStatus = async () => {
    const res = await fetch("/api/status");
    const data = await res.json();
    portStatus.textContent = data.status ? "Åpen" : "Lukket";
    portStatus.className = data.status
      ? "text-xl text-green-600"
      : "text-xl text-red-600";
  };

  const fetchLog = async () => {
    const res = await fetch("/api/log");
    const data = await res.json();
    logList.innerHTML = "";
    data.logs.forEach((entry) => {
      const li = document.createElement("li");
      li.textContent = `[${entry.time}] ${entry.message}`;
      logList.appendChild(li);
    });
  };

  toggleBtn.addEventListener("click", async () => {
    await fetch("/api/toggle", { method: "POST" });
    fetchStatus();
    fetchLog();
  });

  fetchStatus();
  fetchLog();
});
